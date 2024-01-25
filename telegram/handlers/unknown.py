from loguru import logger

from aiogram import Router, F
from aiogram.types import Message
from aiogram.utils.formatting import as_line
from aiogram.enums import ParseMode

from app_globals import app_config, bot


router = Router()


@router.message(F)
@logger.catch
async def cmd_unknown(message: Message):
    logger.debug("-> Enter Def")
    if message.chat.id != bot.chat_id: return

    t = as_line("⁉ Unknown command")
    await message.answer(text=t.as_html(), parse_mode=ParseMode.HTML, request_timeout=app_config['telegram']['sending_timeout_sec'])