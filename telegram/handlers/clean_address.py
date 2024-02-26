from loguru import logger

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode

from aiogram.utils.formatting import as_list

from app_config import app_config
import app_globals


router = Router()


@router.message(Command("clean_address"))
@logger.catch
async def cmd_clean_address(message: Message) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from '{message.from_user.id}'@'{message.chat.id}'")

    t = as_list(
        "🗑 Address wiped!"
    )
    try:
        chat_id = str(message.chat.id)
        app_globals.public_dir.pop(chat_id, None)
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_config['telegram']['sending_timeout_sec']
        )
    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    return
