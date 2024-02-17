from loguru import logger

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.formatting import as_list, as_line, Underline, TextLink, Text
from time import time as t_now

import app_globals

from tools import get_last_seen


class EarningsViewer(StatesGroup):
    waiting_rolls_number = State()


router = Router()


@logger.catch
async def get_earnings(rolls_number: int=1) -> Text:
    logger.debug("-> Enter Def")

    try:
        rolls_number = int(rolls_number)
        if rolls_number < 0 or rolls_number > app_globals.massa_network_values['total_staked_rolls']:
            raise Exception
    except BaseException:
        t = as_list(
            f"‼ Wrong Rolls number value (expected number between 1 and {app_globals.massa_network_values['total_staked_rolls']})", "",
            as_line(
                "☝ Try /view_earnings ",
                Underline("Rolls_number"),
                " command"
            )
        )
        return t

    my_contribution = app_globals.massa_network_values['total_staked_rolls'] / rolls_number
    my_blocks = 172_800 / my_contribution
    my_reward = int(
        my_blocks * app_globals.massa_network_values['block_reward']
    )

    massa_updated = get_last_seen(
        last_time=app_globals.massa_network_values['last_updated'],
        current_time=t_now()
    )

    my_percentage = round(
        (rolls_number / app_globals.massa_network_values['total_staked_rolls']) * 100,
        6
    )

    t = as_list(
        f"🏦 Total number of staked Rolls in MASSA Mainnet: {app_globals.massa_network_values['total_staked_rolls']:,} (updated: {massa_updated})", "",
        f"🍰 Your contribution is: {rolls_number} Rolls ({my_percentage}%)", "",
        f"🪙 Your theoretically MAX earnings ≈ {my_reward} MAS / day", "",
        as_line(
            "👉 ",
            TextLink(
                "More info here",
                url="https://docs.massa.net/docs/learn/tokenomics#example-how-to-compute-my-expected-staking-rewards-"
            )
        )
    )

    return t



@router.message(StateFilter(None), Command("view_earnings"))
@logger.catch
async def cmd_view_earnings(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from user '{message.from_user.id}' in chat '{message.chat.id}'")

    message_list = message.text.split()
    if len(message_list) < 2:
        t = as_list(
            "❓ Please answer with a certain number of staked rolls: ", "",
            f"☝ The answer must be an integer between 0 and {app_globals.massa_network_values['total_staked_rolls']}"
        )
        try:
            await message.reply(
                text=t.as_html(),
                parse_mode=ParseMode.HTML,
                request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
            )
            await state.set_state(EarningsViewer.waiting_rolls_number)
        except BaseException as E:
            logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

        return

    rolls_number = message_list[1]
    t = get_earnings(rolls_number=rolls_number)
    try:
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )
    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    await state.clear()
    return



@router.message(EarningsViewer.waiting_rolls_number, F.text)
@logger.catch
async def show_earnings(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from user '{message.from_user.id}' in chat '{message.chat.id}'")

    rolls_number = message.text
    t = get_earnings(rolls_number=rolls_number)
    try:
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )
    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    await state.clear()
    return
