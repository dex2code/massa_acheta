from loguru import logger

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.formatting import as_list, as_line, TextLink, Code
from aiogram.enums import ParseMode

from app_config import app_config
import app_globals

from tools import save_app_results, check_privacy


class ResetState(StatesGroup):
    reset_sure = State()

router = Router()


@router.message(StateFilter(None), Command("reset"))
@logger.catch
async def cmd_reset(message: Message, state: FSMContext) -> None:
    logger.debug("->Enter Def")
    logger.info(f"-> Got '{message.text}' command from '{message.from_user.id}'@'{message.chat.id}'")
    if not await check_privacy(message=message): return

    t = as_list(
        "⁉ Please confirm that you actually want to reset the service configuration", "",
        "☝ All your configured nodes and wallets will be erased from bot configuration", "",
        as_line(
            "⌨ Type \"",
            Code("I really want to reset all settings"),
            "\" to continue or /cancel to quit the scenario"
        )
    )
    try:
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_config['telegram']['sending_timeout_sec']
        )
        await state.set_state(ResetState.reset_sure)
    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")
        await state.clear()

    return



@router.message(ResetState.reset_sure, F.text)
@logger.catch
async def do_reset(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from '{message.from_user.id}'@'{message.chat.id}'")
    if not await check_privacy(message=message): return

    if message.text.upper() != "I REALLY WANT TO RESET ALL SETTINGS":
        t = as_list(
            "🤚 Reset request rejected", "",
            "👉 Try /help to learn bot commands"
        )
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

    try:
        async with app_globals.results_lock:
            app_globals.app_results = {}
            save_app_results()

    except BaseException as E:
        t = as_list(
            as_line("‼ Error: Could not reset configuration"),
            as_line(
                "💻 Result: ",
                Code(str(E))
            ),
            as_line(
                "⚠ Try again later or watch logs to check the reason - ",
                TextLink(
                    "More info here",
                    url="https://github.com/dex2code/massa_acheta/"
                )
            )
        )

    else:
        t = as_list(
            as_line("👌 Reset done "),
            "👉 You can check new settings using /view_config command"
        )

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
