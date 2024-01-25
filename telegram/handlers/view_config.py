from loguru import logger

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils.formatting import as_list, Pre

from app_globals import app_config, app_results, bot


router = Router()


@router.message(Command("view_config"))
@logger.catch
async def cmd_view_config(message: Message):
    logger.debug("-> Enter Def")
    if message.chat.id != bot.chat_id: return

    nodes_list = ""
    for node_name in app_results:
        node_url = app_results[node_name]['url']
        nodes_list += f"\n• {node_name} ({node_url}):\n"

        for wallet_address in app_results[node_name]['wallets']:
            nodes_list += f"   - {wallet_address}\n"

    if nodes_list == "": nodes_list = "⭕ Nodes list is empty."
    else: nodes_list += "\n"

    t = as_list(
        app_config['telegram']['service_nickname'], "",
        "📋 Current service configuration:",
        Pre(nodes_list),
        "❓ Use /help to learn how to manage settings."
    )
    await message.answer(text=t.as_html(), parse_mode=ParseMode.HTML, request_timeout=app_config['telegram']['sending_timeout_sec'])
