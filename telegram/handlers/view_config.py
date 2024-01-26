from loguru import logger

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils.formatting import as_list, as_line, Pre, Code

from app_globals import app_config, app_results, bot


router = Router()


@router.message(Command("view_config"))
@logger.catch
async def cmd_view_config(message: Message):
    logger.debug("-> Enter Def")
    if message.chat.id != bot.chat_id: return

    config_list = []
    if len(app_results) == 0:
        config_list.append("⭕ Configuration is empty")
    else:
        config_list = []
        for node_name in app_results:
            config_list.append(
                as_line(
                    f"🏠 Node: ",
                    Code(node_name),
                    end=""
                )
            )
            config_list.append(f"🖧 {app_results[node_name]['url']}")

            if len(app_results[node_name]['wallets']) == 0:
                config_list.append("⭕ No wallets attached")
            else:
                config_list.append(f"👛 Wallets attached:")
                for wallet_address in app_results[node_name]['wallets']:
                    config_list.append(Pre(wallet_address))

            config_list.append("")

    t = as_list(
        app_config['telegram']['service_nickname'], "",
        "📋 Current service configuration:", "",
        *config_list,
        "❓ Try /help to learn how to manage settings."
    )
    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        request_timeout=app_config['telegram']['sending_timeout_sec']
    )
