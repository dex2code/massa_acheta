from loguru import logger

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import as_list
from aiogram.enums import ParseMode

import app_globals


router = Router()


@router.message(F)
@logger.catch
async def cmd_unknown(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")

    t = as_list(
        f"⁉ Error: Unknown command \"{message.text}\"", "",
        "👉 Try /help to learn bot commands"
    )
    await message.answer(
        text=t.as_html(),
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=ParseMode.HTML,
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    await state.clear()
    return
