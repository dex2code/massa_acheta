from loguru import logger

import asyncio
from time import time as t_now
from aiogram.utils.formatting import as_list, as_line, Pre, Bold

from app_globals import app_config, app_results
from telegram.queue import queue_telegram_message


async def heartbeat() -> None:
    logger.debug(f"-> Enter Def")

    while True:

        await asyncio.sleep(delay=(app_config['service']['heartbeat_period_hours'] * 60 * 60))
        logger.info(f"Heartbeat planner shedule time")

        composed_node_message = "\n"
        current_time = t_now()

        for node_name in app_results:

            if app_results[node_name]['last_status'] == True:
                node_pic = "🌿 "
                node_status = "Online"
            else:
                node_pic = "☠️ "
                node_status = "Offline"

            last_updated = ""
            if app_results[node_name]['last_update'] == 0:
                last_updated = "Never"
            else:
                diff_time = int(current_time - app_results[node_name]['last_update'])
                diff_hours = diff_time // 3600
                diff_mins = (diff_time - (diff_hours * 3600)) // 60
                last_updated = f"{diff_hours}h {diff_mins}m ago"

            composed_node_message += f" {node_pic} Node {node_name} is {node_status}. Last seen: {last_updated}\n\n"

        t = as_list(
            "⏲ Heartbeat message:", "",
            Pre(composed_node_message),
            as_line("⏳ Heartbeat schedule: every ", Bold(app_config['service']['heartbeat_period_hours']), " hours")
        )
        await queue_telegram_message(message_text=t.as_html())
