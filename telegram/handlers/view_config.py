from loguru import logger

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils.formatting import as_list, as_line, TextLink, Code, as_numbered_list

import app_globals
from tools import get_short_address


router = Router()


@router.message(Command("view_config"))
@logger.catch
async def cmd_view_config(message: Message) -> None:
    logger.debug("-> Enter Def")
    if message.chat.id != app_globals.bot.ACHETA_CHAT: return

    config_list = []

    if len(app_globals.app_results) == 0:
        config_list.append("⭕ Configuration is empty\n")

    else:
        for node_name in app_globals.app_results:
            config_list.append(
                as_line(
                    f"🏠 Node: ",
                    Code(node_name),
                    end=""
                )
            )
            config_list.append(f"📍 {app_globals.app_results[node_name]['url']}")

            if len(app_globals.app_results[node_name]['wallets']) == 0:
                config_list.append("⭕ No wallets attached\n\n")
            else:
                config_list.append(f"👛 {len(app_globals.app_results[node_name]['wallets'])} wallet(s) attached:\n")

                wallet_list = []

                for wallet_address in app_globals.app_results[node_name]['wallets']:
                    wallet_list.append(
                        as_line(
                            TextLink(
                                get_short_address(address=wallet_address),
                                url=f"{app_globals.app_config['service']['mainnet_explorer']}/address/{wallet_address}"
                            )
                        )
                    )

                config_list.append(
                    as_numbered_list(*wallet_list)
                )
                config_list.append("")

    t = as_list(
            as_line(app_globals.app_config['telegram']['service_nickname']),
            "📋 Current service configuration:", "",
            *config_list, 
            "☝ Try /help to learn how to manage settings"
        )
    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    return
