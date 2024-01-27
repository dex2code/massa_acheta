from loguru import logger

import asyncio
from time import time as t_now
from aiogram.utils.formatting import as_list, as_line, Code

import app_globals
from telegram.queue import queue_telegram_message
from tools import get_last_seen


async def heartbeat() -> None:
    logger.debug(f"-> Enter Def")

    while True:

        await asyncio.sleep(delay=(app_globals.app_config['service']['heartbeat_period_hours'] * 60 * 60))
        logger.info(f"Heartbeat planner shedule time")

        current_time = t_now()

        heartbeat_list = []
        if len(app_globals.app_results) == 0:
            heartbeat_list.append("⭕ Node list is empty.\n")
        else:
            for node_name in app_globals.app_results:
                if app_globals.app_results[node_name]['last_status'] == True: node_status = "🌿 Online"
                else: node_status = "☠️ Offline"

                last_seen = get_last_seen(
                    last_time=app_globals.app_results[node_name]['last_update'],
                    current_time=current_time
                )

                heartbeat_list.append(as_line(f"🏠 Node: ", Code(node_name), end=""))
                heartbeat_list.append(f"📍 {app_globals.app_results[node_name]['url']}")
                heartbeat_list.append(f"{node_status} (Last seen: {last_seen})\n")

        t = as_list(
            "⏲ Heartbeat message:", "",
            *heartbeat_list,
            f"⏳ Heartbeat schedule: every {app_globals.app_config['service']['heartbeat_period_hours']} hours")
        await queue_telegram_message(message_text=t.as_html())
