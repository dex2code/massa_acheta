from loguru import logger
logger.add(
    "main.log",
    format="\"{time}\", \"{level}\", \"{file}:{line}\", \"{module}:{function}\", \"{message}\"",
    level="INFO",
    rotation="1 week",
    compression="zip",
    enqueue=True,
    backtrace=True,
    diagnose=True
)

import asyncio
import json
from aiogram.utils.formatting import as_list
from aiogram.types import BotCommand

import app_globals

from remotes.monitor import monitor as remote_monitor
from remotes.massa import massa as remote_massa
from remotes.heartbeat import heartbeat as remote_heartbeat

from telegram.queue import queue_telegram_message, operate_telegram_queue

from telegram.handlers import start
from telegram.handlers import cancel
from telegram.handlers import view_config, view_node, view_wallet, view_address, view_credits
from telegram.handlers import add_node, add_wallet
from telegram.handlers import delete_node, delete_wallet
from telegram.handlers import massa_info, acheta_release
from telegram.handlers import ping, id
from telegram.handlers import reset
from telegram.handlers import unknown


@logger.catch
async def main() -> None:
    logger.debug(f"-> Enter Def")

    bot_commands = [
        BotCommand(command="/help", description="Show help info"),
        BotCommand(command="/view_config", description="View service config"),
        BotCommand(command="/view_node", description="View node status"),
        BotCommand(command="/view_wallet", description="View wallet info"),
        BotCommand(command="/view_address", description="View any wallet info"),
        BotCommand(command="/view_credits", description="View any wallet credits"),
        BotCommand(command="/add_node", description="Add node to bot"),
        BotCommand(command="/add_wallet", description="Add wallet to bot"),
        BotCommand(command="/delete_node", description="Delete node from bot"),
        BotCommand(command="/delete_wallet", description="Delete wallet from bot"),
        BotCommand(command="/massa_info", description="Show MASSA network info"),
        BotCommand(command="/acheta_release", description="Actual Acheta release"),
        BotCommand(command="/ping", description="Pong!"),
        BotCommand(command="/id", description="Show your TG ID"),
        BotCommand(command="/cancel", description="Cancel ongoing scenario"),
        BotCommand(command="/reset", description="Reset bot configuration")
    ]
    await app_globals.tg_bot.set_my_commands(bot_commands)

    nodes_list = []

    if len(app_globals.app_results) == 0:
        nodes_list.append("\n⭕ Node list is empty")
    else:
        for node_name in app_globals.app_results:
            nodes_list.append(f"\n🏠 Node: \"{node_name}\"")
            nodes_list.append(f"📍 {app_globals.app_results[node_name]['url']}")
            nodes_list.append(f"👛 {len(app_globals.app_results[node_name]['wallets'])} wallet(s) attached")


    t = as_list(
        "🔆 Service successfully started to watch the following nodes:",
        *nodes_list, "",
        "👉 Try /help to learn bot commands", "",
        f"⏳ Main loop period: {app_globals.app_config['service']['main_loop_period_sec']} seconds",
        f"⚡ Probe timeout: {app_globals.app_config['service']['http_probe_timeout_sec']} seconds"
    )
    await queue_telegram_message(message_text=t.as_html())

    aio_loop = asyncio.get_event_loop()
    aio_loop.create_task(operate_telegram_queue())
    aio_loop.create_task(remote_monitor())
    aio_loop.create_task(remote_massa())
    aio_loop.create_task(remote_heartbeat())


    app_globals.tg_dp.include_router(start.router)

    app_globals.tg_dp.include_router(cancel.router)

    app_globals.tg_dp.include_router(view_config.router)
    app_globals.tg_dp.include_router(view_node.router)
    app_globals.tg_dp.include_router(view_wallet.router)
    app_globals.tg_dp.include_router(view_address.router)
    app_globals.tg_dp.include_router(view_credits.router)

    app_globals.tg_dp.include_router(add_node.router)
    app_globals.tg_dp.include_router(add_wallet.router)

    app_globals.tg_dp.include_router(delete_node.router)
    app_globals.tg_dp.include_router(delete_wallet.router)

    app_globals.tg_dp.include_router(massa_info.router)
    app_globals.tg_dp.include_router(acheta_release.router)

    app_globals.tg_dp.include_router(ping.router)
    app_globals.tg_dp.include_router(id.router)

    app_globals.tg_dp.include_router(reset.router)

    app_globals.tg_dp.include_router(unknown.router)

    await app_globals.tg_bot.delete_webhook(drop_pending_updates=True)
    await app_globals.tg_dp.start_polling(app_globals.tg_bot)

    return




if __name__ == "__main__":
    logger.debug(f"Config:\n{json.dumps(obj=app_globals.app_config, indent=4)}")
    logger.debug(f"Results:\n{json.dumps(obj=app_globals.app_results, indent=4)}")

    asyncio.run(main())
