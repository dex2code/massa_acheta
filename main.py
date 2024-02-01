from loguru import logger
logger.add("main.log", format="\"{time}\", \"{level}\", \"{file}:{line}\", \"{module}:{function}\", \"{message}\"", level="INFO", rotation="1 week", compression="zip")

import asyncio
import json
from aiogram.utils.formatting import as_list, as_line, Code
from aiogram.types import BotCommand

import app_globals

from remotes.heartbeat import heartbeat as remote_heartbeat
from remotes.releases import releases as remote_releases
from remotes.monitor import monitor as remote_monitor

from telegram.queue import queue_telegram_message, operate_telegram_queue

from telegram.handlers import start
from telegram.handlers import view_config, view_node, view_wallet, view_address
from telegram.handlers import delete_node, delete_wallet
from telegram.handlers import massa_release, acheta_release
from telegram.handlers import ping, id, cancel, unknown


@logger.catch
async def main() -> None:
    logger.debug(f"-> Enter Def")

    bot_commands = [
        BotCommand(command="/help", description="Help page"), # Done!
        BotCommand(command="/view_config", description="View service config"), # Done!
        BotCommand(command="/view_node", description="View node status"), # Done!
        BotCommand(command="/view_wallet", description="View wallet info"), # Done!
        BotCommand(command="/view_address", description="View any wallet info"), # Done!
        BotCommand(command="/add_node", description="Add node to bot"),
        BotCommand(command="/add_wallet", description="Add wallet to bot"),
        BotCommand(command="/delete_node", description="Delete node from bot"), # Done!
        BotCommand(command="/delete_wallet", description="Delete wallet from bot"), # Done!
        BotCommand(command="/massa_release", description="Show latest MASSA release"), # Done!
        BotCommand(command="/acheta_release", description="Show latest Acheta release"), # Done!
        BotCommand(command="/ping", description="Pong!"), # Done!
        BotCommand(command="/id", description="Show User and Chat ID"), # Done!
        BotCommand(command="/cancel", description="Cancel any scenario") # Done!
    ]

    await app_globals.tg_bot.set_my_commands(bot_commands)

    nodes_list = []

    if len(app_globals.app_results) == 0:
        nodes_list.append("⭕ Node list is empty")
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
    aio_loop.create_task(remote_releases())


    app_globals.tg_dp.include_router(start.router)

    app_globals.tg_dp.include_router(view_config.router)
    app_globals.tg_dp.include_router(view_node.router)
    app_globals.tg_dp.include_router(view_wallet.router)
    app_globals.tg_dp.include_router(view_address.router)

    app_globals.tg_dp.include_router(delete_node.router)
    app_globals.tg_dp.include_router(delete_wallet.router)

    app_globals.tg_dp.include_router(massa_release.router)
    app_globals.tg_dp.include_router(acheta_release.router)

    app_globals.tg_dp.include_router(ping.router)
    app_globals.tg_dp.include_router(id.router)
    app_globals.tg_dp.include_router(cancel.router)

    app_globals.tg_dp.include_router(unknown.router)

    await app_globals.tg_bot.delete_webhook(drop_pending_updates=True)
    await app_globals.tg_dp.start_polling(app_globals.tg_bot)

    return




if __name__ == "__main__":
    logger.info(f"*** MASSA Acheta starting service...")

    for node_name in app_globals.app_results:
        app_globals.app_results[node_name]['last_status'] = "unknown"
        app_globals.app_results[node_name]['last_update'] = 0
        app_globals.app_results[node_name]['last_result'] = {"unknown": "Never updated before"}

        for wallet_address in app_globals.app_results[node_name]['wallets']:
            app_globals.app_results[node_name]['wallets'][wallet_address] = {}
            app_globals.app_results[node_name]['wallets'][wallet_address]['final_balance'] = 0
            app_globals.app_results[node_name]['wallets'][wallet_address]['candidate_rolls'] = 0
            app_globals.app_results[node_name]['wallets'][wallet_address]['active_rolls'] = 0
            app_globals.app_results[node_name]['wallets'][wallet_address]['missed_blocks'] = 0
            app_globals.app_results[node_name]['wallets'][wallet_address]['last_status'] = "unknown"
            app_globals.app_results[node_name]['wallets'][wallet_address]['last_update'] = 0
            app_globals.app_results[node_name]['wallets'][wallet_address]['last_result'] = {"unknown": "Never updated before"}

    logger.debug(f"Results file loaded successfully:\n {json.dumps(obj=app_globals.app_results, indent=4)}")
    logger.info(f"Watching nodes with {app_globals.app_config['service']['main_loop_period_sec']} seconds loop period and {app_globals.app_config['service']['http_probe_timeout_sec']} seconds probe timeout.")
    logger.info(f"*** Service successfully started!")

    asyncio.run(main())
