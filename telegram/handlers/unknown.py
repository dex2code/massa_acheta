from loguru import logger

from aiogram import Router, F
from aiogram.types import Message

from app_globals import app_config


router = Router()


@router.message(F)
@logger.catch
async def cmd_unknown(message: Message):
    logger.debug("-> Enter Def")
    if message.chat.id != app_config['telegram']['chat_id']: return

    await message.answer(text="⁉ Unknown command")