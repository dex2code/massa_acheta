from loguru import logger

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils.formatting import as_list, as_line, Code

import app_globals


router = Router()


@router.message(Command("acheta_release"))
@logger.catch
async def cmd_acheta_release(message: Message) -> None:
    logger.debug("-> Enter Def")
    if message.chat.id != app_globals.bot.chat_id: return

    t = as_list(
            as_line(app_globals.app_config['telegram']['service_nickname']),
            as_line(
                "🦗 Latest released ACHETA version: ",
                Code(app_globals.latest_acheta_release)
            ),
            as_line(
                "💾 You have version: ",
                Code(app_globals.local_acheta_release)
            ),
            as_line(f"⏳ Service checks releases: every {int(app_globals.app_config['service']['main_loop_period_sec'] / 2)} seconds")
        )
    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    return