from loguru import logger

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils.formatting import as_list, as_line, Code

from app_globals import bot, current_massa_release, app_config


router = Router()


@router.message(Command("release"))
@logger.catch
async def cmd_cancel(message: Message):
    logger.debug("-> Enter Def")
    if message.chat.id != bot.chat_id: return

    t = as_list(
        app_config['telegram']['service_nickname'], "",
        as_line("💾 Latest released MASSA version: ", Code(current_massa_release)),
        as_line(f"⏳ Service checks releases: every {int(app_config['service']['main_loop_period_sec'] / 2)} seconds")
    )
    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        request_timeout=app_config['telegram']['sending_timeout_sec']
    )
