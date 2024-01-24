from loguru import logger

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app_globals import app_config


router = Router()


@router.message(Command("start", "help"))
@logger.catch
async def cmd_start(message: Message):
    logger.debug("-> Enter Def")
    if message.chat.id != app_config['telegram']['chat_id']: return

    await message.answer(text="I am start or help")