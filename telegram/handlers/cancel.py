from loguru import logger

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import as_list

import app_globals


router = Router()


@router.message(Command("cancel"))
@logger.catch
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"Got '{message.text}' command from user '{message.chat.id}'")

    t = as_list(
        "❌ Action cancelled!"
    )
    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove(),
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    await state.clear()
    return
