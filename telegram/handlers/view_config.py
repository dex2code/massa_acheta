from loguru import logger

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils.formatting import as_list, as_line, TextLink

from app_config import app_config
import app_globals

from tools import get_short_address, check_privacy, get_last_seen


router = Router()


@router.message(StateFilter(None), Command("view_config"))
@logger.catch
async def cmd_view_config(message: Message) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from '{message.from_user.id}'@'{message.chat.id}'")
    if not await check_privacy(message=message): return

    config_list = []

    if len(app_globals.app_results) == 0:
        config_list.append("⭕ Configuration is empty\n")

    else:
        for node_name in app_globals.app_results:
            config_list.append(f"🏠 Node: \"{node_name}\"")
            config_list.append(f"📍 {app_globals.app_results[node_name]['url']}")

            if len(app_globals.app_results[node_name]['wallets']) == 0:
                config_list.append("⭕ No wallets attached\n")
            else:
                config_list.append(f"👛 {len(app_globals.app_results[node_name]['wallets'])} wallet(s) attached:")

                wallet_list = []

                for wallet_address in app_globals.app_results[node_name]['wallets']:
                    wallet_list.append(
                        as_line(
                            "⦙\n",
                            "⦙… ",
                            TextLink(
                                await get_short_address(address=wallet_address),
                                url=f"{app_config['service']['mainnet_explorer_url']}/address/{wallet_address}"
                            ),
                            end=""
                        )
                    )
                wallet_list.append("")
                config_list.append(
                    as_list(*wallet_list)
                )

    t = as_list(
        "📋 Current service configuration:", "",
        *config_list,
        f"🏃 Bot started: {await get_last_seen(last_time=app_globals.acheta_start_time, show_days=True)}", "",
        "👉 Try /help to learn how to manage settings"
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
