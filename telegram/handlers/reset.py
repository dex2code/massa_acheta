from loguru import logger

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.formatting import as_list, as_line, TextLink, Code
from aiogram.enums import ParseMode

import app_globals
from tools import save_app_results


class ResetState(StatesGroup):
    reset_sure = State()


router = Router()


@router.message(StateFilter(None), Command("reset"))
@logger.catch
async def cmd_reset(message: Message, state: FSMContext) -> None:
    logger.debug("->Enter Def")
    if message.chat.id != app_globals.bot.chat_id: return

    t = as_list(
            as_line(app_globals.app_config['telegram']['service_nickname']),
            "⁉ Please confirm that you actually want to reset the service configuration", "",
            "☝ All your configured nodes and wallets will be erased from bot configuration", "",
            as_line(
                "⌨ Type \"",
                Code("I want to reset the service"),
                "\" to continue or /cancel to quit the scenario"
            )
        )
    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    await state.set_state(ResetState.reset_sure)
    return



@router.message(ResetState.reset_sure, F.text)
@logger.catch
async def do_reset(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    if message.chat.id != app_globals.bot.chat_id: return

    if message.text.upper() != "I WANT TO RESET THE SERVICE":
        t = as_list(
                as_line(app_globals.app_config['telegram']['service_nickname']),
                "🙆 Reset request rejected", "",
                "☝ Try /help to learn bot commands"
            )
        await message.answer(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )

        await state.clear()
        return

    try:
        async with app_globals.results_lock:
            app_globals.app_results = {}
            await save_app_results()

    except Exception as E:
        t = as_list(
                as_line(app_globals.app_config['telegram']['service_nickname']),
                as_line("‼ Error: Could not reset configuration"),
                as_line(
                    "💻 Result: ",
                    Code(str(E))
                ),
                as_line(
                    "⚠ Try again later or watch logs to check the reason - ",
                    TextLink(
                        "More info here",
                        url="https://github.com/dex2code/massa_acheta/blob/main/README.md"
                    )
                )
            )

    else:
        t = as_list(
                as_line(app_globals.app_config['telegram']['service_nickname']),
                as_line("✅ Reset done "),
                "☝ You can check new settings using /view_config command"
            )


    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    await state.clear()
    return
