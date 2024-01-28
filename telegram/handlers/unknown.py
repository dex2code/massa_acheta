from loguru import logger

from aiogram import Router, F
from aiogram.types import Message
from aiogram.utils.formatting import as_list, as_line
from aiogram.enums import ParseMode

import app_globals


router = Router()


@router.message(F)
@logger.catch
async def cmd_unknown(message: Message) -> None:
    logger.debug("-> Enter Def")
    if message.chat.id != app_globals.bot.chat_id: return

    t = as_list(
        as_line(app_globals.app_config['telegram']['service_nickname']),
        "⁉ Unknown command.", "",
        "Try /cancel to quit ongoing scenario or /help to learn correct commands."
    )
    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    return
