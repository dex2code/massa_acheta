from loguru import logger

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.formatting import as_list, as_line, Bold
from aiogram.enums import ParseMode

from app_globals import app_config, bot


router = Router()


@router.message(Command("start", "help"))
@logger.catch
async def cmd_start(message: Message):
    logger.debug("-> Enter Def")
    if message.chat.id != bot.chat_id: return

    t = as_list(
        app_config['telegram']['service_nickname'], "",

        as_line(Bold('📖 Commands'), ":"), ""

        "  ⦙  /start or /help  →  This message", "",

        "  ⦙  /view_config  →  View active service config",
        "  ⦙  /view_node  →  View a node status",
        "  ⦙  /view_wallet  →  View a wallet info",
        "  ⦙  /view_address  →  View any wallet address info", "",

        "  ⦙  /add_node  →  Add a node to bot",
        "  ⦙  /add_wallet  →  Add a wallet to bot", "",

        "  ⦙  /delete_node  →  Delete node from bot",
        "  ⦙  /delete_wallet  →  Delete wallet from bot", "",

        "  ⦙  /cancel  →  Cancel any ongoing scenario",


        as_line("☝ ", Bold("Bot info"), ": https://github.com/dex2code/massa_acheta")
    )

    await message.answer(text=t.as_html(), parse_mode=ParseMode.HTML, request_timeout=app_config['telegram']['sending_timeout_sec'])