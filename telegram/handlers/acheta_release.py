from loguru import logger

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils.formatting import as_list, as_line, TextLink

from app_config import app_config
import app_globals

from tools import check_privacy


router = Router()


@router.message(StateFilter(None), Command("acheta_release"))
@logger.catch
async def cmd_acheta_release(message: Message) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from '{message.from_user.id}'@'{message.chat.id}'")
    if not await check_privacy(message=message): return

    if app_globals.latest_acheta_release == app_globals.local_acheta_release:
        update_needed = as_line("👌 No updates needed")
    else:
        update_needed = as_line(
            "☝ Please update your bot - ",
            TextLink(
                "More info here",
                url="https://github.com/dex2code/massa_acheta/"
            )
        )

    t = as_list(
        f"🦗 Latest released ACHETA version: \"{app_globals.latest_acheta_release}\"",
        f"💾 You have version: \"{app_globals.local_acheta_release}\"", "",
        update_needed,
        as_line(f"⏳ Service checks releases: every {app_config['service']['main_loop_period_min']} minutes")
    )
    try:
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_config['telegram']['sending_timeout_sec']
        )
    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    return
