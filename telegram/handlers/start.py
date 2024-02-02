from loguru import logger

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.formatting import as_list, as_line, TextLink
from aiogram.enums import ParseMode

import app_globals


router = Router()


@router.message(Command("start", "help"))
@logger.catch
async def cmd_start(message: Message) -> None:
    logger.debug("-> Enter Def")
    if message.chat.id != app_globals.bot.ACHETA_CHAT: return

    t = as_list(
            as_line(app_globals.app_config['telegram']['service_nickname']),
            "📖 Commands:", "",
            " ⦙ /start or /help ⋅ This message", "",
            " ⦙ /view_config ⋅ View service config", "",
            " ⦙ /view_node ⋅ View node status", "",
            " ⦙ /view_wallet ⋅ View wallet info", "",
            " ⦙ /view_address ⋅ View any wallet info", "",
            " ⦙ /add_node ⋅ Add node to bot", "",
            " ⦙ /add_wallet ⋅ Add wallet to bot", "",
            " ⦙ /delete_node ⋅ Delete node from bot", "",
            " ⦙ /delete_wallet ⋅ Delete wallet from bot", "",
            " ⦙ /massa_release ⋅ Show actual MASSA release", "",
            " ⦙ /acheta_release ⋅ Show actual Acheta release", "",
            " ⦙ /ping ⋅ Pong!", "",
            " ⦙ /id ⋅ Show User and Chat ID", "",
            " ⦙ /cancel ⋅ Cancel any scenario", "",
            as_line(
                "☝ ",
                TextLink(
                    "More info here",
                    url="https://github.com/dex2code/massa_acheta/blob/main/README.md"
                )
            )
        )

    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    return
