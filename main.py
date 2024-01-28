from loguru import logger
logger.add("main.log", format="\"{time}\", \"{level}\", \"{file}:{line}\", \"{module}:{function}\", \"{message}\"", level="INFO", rotation="1 week", compression="zip")

import asyncio
import json
from aiogram.utils.formatting import as_list, as_line, Code

import app_globals

from remotes.heartbeat import heartbeat as remote_heartbeat
from remotes.github_releases import release as remote_github_release
from remotes.monitor import monitor as remote_monitor

from telegram.queue import queue_telegram_message, operate_telegram_queue

from telegram.handlers import start
from telegram.handlers import view_config, view_node, view_wallet
from telegram.handlers import massa_release
from telegram.handlers import id, cancel, unknown


@logger.catch
async def main() -> None:
    logger.debug(f"-> Enter Def")

    nodes_list = []

    if len(app_globals.app_results) == 0:
        nodes_list.append("⭕ Node list is empty.")
    else:
        for node_name in app_globals.app_results:
            nodes_list.append(
                as_line(
                    "\n",
                    "🏠 Node: ",
                    Code(node_name),
                    end=""
                )
            )
            nodes_list.append(f"📍 {app_globals.app_results[node_name]['url']}")
            nodes_list.append(f"👛 {len(app_globals.app_results[node_name]['wallets'])} wallet(s) attached")


    t = as_list(
        "🔆 Service successfully started to watch the following nodes:",
        *nodes_list, "",
        "❓ Try /help to learn how to manage settings", "",
        f"⏳ Main loop period: {app_globals.app_config['service']['main_loop_period_sec']} seconds",
        f"⚡ Probe timeout: {app_globals.app_config['service']['http_probe_timeout_sec']} seconds"
    )
    await queue_telegram_message(message_text=t.as_html())

    aio_loop = asyncio.get_event_loop()
    aio_loop.create_task(operate_telegram_queue())
    aio_loop.create_task(remote_monitor())
    aio_loop.create_task(remote_heartbeat())
    aio_loop.create_task(remote_github_release())


    app_globals.tg_dp.include_router(start.router)

    app_globals.tg_dp.include_router(view_config.router)
    app_globals.tg_dp.include_router(view_node.router)
    app_globals.tg_dp.include_router(view_wallet.router)

    app_globals.tg_dp.include_router(massa_release.router)

    app_globals.tg_dp.include_router(id.router)
    app_globals.tg_dp.include_router(cancel.router)

    app_globals.tg_dp.include_router(unknown.router)

    await app_globals.tg_bot.delete_webhook(drop_pending_updates=True)
    await app_globals.tg_dp.start_polling(app_globals.tg_bot)




if __name__ == "__main__":
    logger.info(f"*** MASSA Acheta starting service...")

    for node_name in app_globals.app_results:
        app_globals.app_results[node_name]['last_status'] = "unknown"
        app_globals.app_results[node_name]['last_update'] = 0
        app_globals.app_results[node_name]['last_result'] = {"unknown": "Never updated before"}

        for wallet_addr in app_globals.app_results[node_name]['wallets']:
            app_globals.app_results[node_name]['wallets'][wallet_addr] = {}
            app_globals.app_results[node_name]['wallets'][wallet_addr]['final_balance'] = 0
            app_globals.app_results[node_name]['wallets'][wallet_addr]['candidate_rolls'] = 0
            app_globals.app_results[node_name]['wallets'][wallet_addr]['active_rolls'] = 0
            app_globals.app_results[node_name]['wallets'][wallet_addr]['missed_blocks'] = 0
            app_globals.app_results[node_name]['wallets'][wallet_addr]['last_status'] = "unknown"
            app_globals.app_results[node_name]['wallets'][wallet_addr]['last_update'] = 0
            app_globals.app_results[node_name]['wallets'][wallet_addr]['last_result'] = {"unknown": "Never updated before"}

    logger.debug(f"Results file loaded successfully:\n {json.dumps(obj=app_globals.app_results, indent=4)}")
    logger.info(f"Watching nodes with {app_globals.app_config['service']['main_loop_period_sec']} seconds loop period and {app_globals.app_config['service']['http_probe_timeout_sec']} seconds probe timeout.")
    logger.info(f"*** Service successfully started!")

    asyncio.run(main())
