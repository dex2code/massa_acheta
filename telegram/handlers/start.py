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

    if message.chat.id != app_globals.bot.ACHETA_CHAT:
        t = as_list(
                as_line("📖 Commands:"),
                as_line(" ⦙ /start or /help ⋅ This message"),
                as_line(" ⦙ /view_address ⋅ View any wallet info"),
                as_line(" ⦙ /massa_release ⋅ Show actual MASSA release"),
                as_line(" ⦙ /ping ⋅ Pong!"),
                as_line(" ⦙ /id ⋅ Show User and Chat ID"),
                as_line(" ⦙ /cancel ⋅ Cancel ongoing scenario"),
                as_line(
                    "👉 ",
                    TextLink(
                        "More info here",
                        url="https://github.com/dex2code/massa_acheta/"
                    )
                )
            )

    else:
        t = as_list(
                as_line("📖 Commands:"),
                as_line(" ⦙ /start or /help ⋅ This message"),
                as_line(" ⦙ /view_config ⋅ View service config"),
                as_line(" ⦙ /view_node ⋅ View node status"),
                as_line(" ⦙ /view_wallet ⋅ View wallet info"),
                as_line(" ⦙ /view_address ⋅ View any wallet info"),
                as_line(" ⦙ /add_node ⋅ Add node to bot"),
                as_line(" ⦙ /add_wallet ⋅ Add wallet to bot"),
                as_line(" ⦙ /delete_node ⋅ Delete node from bot"),
                as_line(" ⦙ /delete_wallet ⋅ Delete wallet from bot"),
                as_line(" ⦙ /massa_release ⋅ Show actual MASSA release"),
                as_line(" ⦙ /acheta_release ⋅ Show actual Acheta release"),
                as_line(" ⦙ /ping ⋅ Pong!"),
                as_line(" ⦙ /id ⋅ Show User and Chat ID"),
                as_line(" ⦙ /cancel ⋅ Cancel ongoing scenario"),
                as_line(" ⦙ /reset ⋅ Reset service configuration"),
                as_line(
                    "👉 ",
                    TextLink(
                        "More info here",
                        url="https://github.com/dex2code/massa_acheta/"
                    )
                )
            )

    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    return
