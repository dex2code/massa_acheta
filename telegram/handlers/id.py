from loguru import logger

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils.formatting import as_list

from app_globals import app_config


router = Router()


@router.message(Command("id"))
@logger.catch
async def cmd_cancel(message: Message):
    logger.debug("-> Enter Def")

    t = as_list(
        app_config['telegram']['service_nickname'], "",
        f"👤 User ID: {message.from_user.id}", "",
        f"💬 Chat ID: {message.chat.id}",
    )
    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        request_timeout=app_config['telegram']['sending_timeout_sec']
    )
