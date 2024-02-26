from loguru import logger

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.formatting import as_list, as_line, Underline, TextLink, Text

from app_config import app_config
import app_globals

from tools import get_last_seen, get_rewards_mas_day


class EarningsViewer(StatesGroup):
    waiting_rolls_number = State()

router = Router()


@logger.catch
async def get_earnings(rolls_number: int=1) -> Text:
    logger.debug("-> Enter Def")

    try:
        rolls_number = int(rolls_number)
        if rolls_number < 1 or rolls_number > app_globals.massa_network['values']['total_staked_rolls']:
            raise Exception

    except BaseException:
        return as_list(
            f"‼ Wrong Rolls number value (expected number between 1 and {app_globals.massa_network['values']['total_staked_rolls']})", "",
            as_line(
                "☝ Try /view_earnings ",
                Underline("Rolls_number"),
                " command"
            )
        )

    else:
        computed_rewards = await get_rewards_mas_day(rolls_number=rolls_number)

        massa_updated = await get_last_seen(
            last_time=app_globals.massa_network['values']['last_updated']
        )

        my_percentage = round(
            (rolls_number / app_globals.massa_network['values']['total_staked_rolls']) * 100,
            6
        )

        return as_list(
            f"🏦 Total number of staked Rolls in MASSA Mainnet: {app_globals.massa_network['values']['total_staked_rolls']:,} (updated: {massa_updated})", "",
            f"🍰 Your contribution is: {rolls_number:,} Rolls ({my_percentage}%)", "",
            f"🪙 Your estimated earnings ≈ {computed_rewards:,} MAS / Day", "",
            as_line(
                "👉 ",
                TextLink(
                    "More info here",
                    url="https://docs.massa.net/docs/learn/tokenomics#example-how-to-compute-my-expected-staking-rewards-"
                )
            )
        )



@router.message(StateFilter(None), Command("view_earnings"))
@logger.catch
async def cmd_view_earnings(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from '{message.from_user.id}'@'{message.chat.id}'")

    message_list = message.text.split()
    if len(message_list) < 2:
        t = as_list(
            "❓ Please answer with a certain number of staked rolls: ", "",
            f"☝ The answer must be an integer between 1 and {app_globals.massa_network['values']['total_staked_rolls']}", "",
            "👉 Use /cancel to quit the scenario"
        )
        try:
            await message.reply(
                text=t.as_html(),
                parse_mode=ParseMode.HTML,
                request_timeout=app_config['telegram']['sending_timeout_sec']
            )
            await state.set_state(EarningsViewer.waiting_rolls_number)
        except BaseException as E:
            logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

        return

    rolls_number = message_list[1]
    t = await get_earnings(rolls_number=rolls_number)
    try:
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_config['telegram']['sending_timeout_sec']
        )
    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    await state.clear()
    return



@router.message(EarningsViewer.waiting_rolls_number, F.text)
@logger.catch
async def show_earnings(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from '{message.from_user.id}'@'{message.chat.id}'")

    rolls_number = "0"
    command_list = message.text.split()
    for cmd in command_list:
        if cmd.isdigit():
            rolls_number = cmd
            break

    t = await get_earnings(rolls_number=rolls_number)
    try:
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_config['telegram']['sending_timeout_sec']
        )
    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    await state.clear()
    return
