from loguru import logger

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.enums import ParseMode

from app_globals import app_config


router = Router()


@router.message(Command("cancel"))
@logger.catch
async def cmd_cancel(message: Message):
    logger.debug("-> Enter Def")
    if message.chat.id != app_config['telegram']['chat_id']: return

    message_text = "❌ Action cancelled!"

    await message.answer(text=message_text, parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove())