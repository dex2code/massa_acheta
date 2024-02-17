from loguru import logger

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils.formatting import as_list, as_line, Code

import app_globals


router = Router()


@router.message(StateFilter(None), Command("view_id"))
@logger.catch
async def cmd_view_id(message: Message) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from user '{message.from_user.id}' in chat '{message.chat.id}'")

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
    try:
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )
    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    return
