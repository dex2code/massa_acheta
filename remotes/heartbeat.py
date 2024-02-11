from loguru import logger

import asyncio
from time import time as t_now
from aiogram.utils.formatting import as_list, as_line, TextLink, as_numbered_list

import app_globals
from telegram.queue import queue_telegram_message
from tools import get_last_seen, get_short_address


async def heartbeat() -> None:
    logger.debug(f"-> Enter Def")

    while True:

        logger.info(f"Sleeping for {app_globals.app_config['service']['heartbeat_period_hours'] * 60 * 60} seconds...")
        await asyncio.sleep(delay=(app_globals.app_config['service']['heartbeat_period_hours'] * 60 * 60))
        logger.info(f"Heartbeat planner shedule time")

        current_time = t_now()

        heartbeat_list = []

        if len(app_globals.app_results) == 0:
            heartbeat_list.append("⭕ Node list is empty\n")

        else:

            for node_name in app_globals.app_results:
                heartbeat_list.append(f"🏠 Node: \"{node_name}\"")
                heartbeat_list.append(f"📍 {app_globals.app_results[node_name]['url']}")

                last_seen = get_last_seen(
                    last_time=app_globals.app_results[node_name]['last_update'],
                    current_time=current_time
                )

                if app_globals.app_results[node_name]['last_status'] == True:
                    heartbeat_list.append(f"🌿 Status: Online ({last_seen})")

                    num_wallets = len(app_globals.app_results[node_name]['wallets'])
                    if num_wallets == 0:
                        heartbeat_list.append("⭕ No wallets attached\n")
                    else:
                        heartbeat_list.append(f"👛 {num_wallets} wallet(s) attached:\n")

                        wallet_list = []

                        for wallet_address in app_globals.app_results[node_name]['wallets']:

                            if app_globals.app_results[node_name]['wallets'][wallet_address]['last_status'] == True:
                                wallet_list.append(
                                    as_line(
                                        TextLink(
                                            get_short_address(address=wallet_address),
                                            url=f"{app_globals.app_config['service']['mainnet_explorer_url']}/address/{wallet_address}"
                                        ),
                                        f" ( {app_globals.app_results[node_name]['wallets'][wallet_address]['final_balance']:,} MAS )"
                                    )
                                )
                            else:
                                wallet_list.append(
                                    as_line(
                                        TextLink(
                                            get_short_address(address=wallet_address),
                                            url=f"{app_globals.app_config['service']['mainnet_explorer_url']}/address/{wallet_address}"
                                        ),
                                        " ( Unknown MAS )"
                                    )
                                )
                        
                        heartbeat_list.append(as_numbered_list(*wallet_list))

                else:
                    heartbeat_list.append(f"☠️ Status: Offline ({last_seen})")
                    heartbeat_list.append("⭕ No wallets info available")

                heartbeat_list.append("")

        t = as_list(
            "💓 Heartbeat message:", "",
            *heartbeat_list,
            f"⏳ Heartbeat schedule: every {app_globals.app_config['service']['heartbeat_period_hours']} hour(s)"
        )
        await queue_telegram_message(message_text=t.as_html())
