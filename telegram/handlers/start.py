from loguru import logger

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.formatting import as_list, Bold
from aiogram.enums import ParseMode

from app_globals import app_config


router = Router()


@router.message(Command("start", "help"))
@logger.catch
async def cmd_start(message: Message):
    logger.debug("-> Enter Def")
    if message.chat.id != app_config['telegram']['chat_id']: return

    message_text = as_list(
        app_config['telegram']['service_nickname'], "",

        Bold("📖 Commands:"), "",

        "  ⦙  /start or /help  →  This message",
        "  ⦙  /view_config  →  View active service config",
        "  ⦙  /cancel  →  Cancel ongoing scenario", "",

        "  ⦙  /view_node  →  View a node status",
        "  ⦙  /view_wallet  →  View a wallet info",
        "  ⦙  /view_address  →  View any wallet address info", "",

        "  ⦙  /add_node  →  Add a node to bot",
        "  ⦙  /add_wallet  →  Add a wallet to bot", "",

        "  ⦙  /delete_node  →  Delete node from bot",
        "  ⦙  /delete_wallet  →  Delete wallet from bot", "",

        "☝ <b>Bot info</b>: https://github.com/dex2code/massa_acheta"
    )

    await message.answer(text=message_text.as_html(), parse_mode=ParseMode.HTML)