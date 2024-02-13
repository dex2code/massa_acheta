from loguru import logger

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils.formatting import as_list, as_line, Code

import app_globals


router = Router()


@router.message(Command("id"))
@logger.catch
async def cmd_cancel(message: Message) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from user '{message.chat.id}'")

    t = as_list(
        as_line(
            "👤 User ID: ",
            Code(message.from_user.id)
        ),
        as_line(
            "💬 Chat ID: ",
            Code(message.chat.id)
        )
    )
    await message.reply(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    return
