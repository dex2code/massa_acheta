from loguru import logger
logger.add("main.log", format="\"{time}\", \"{level}\", \"{file}:{line}\", \"{module}:{function}\", \"{message}\"", level="INFO", rotation="1 week", compression="zip")

import asyncio
import json
from aiogram import types
from aiogram.filters import CommandStart
from aiogram.types import Message

from app_init import app_config, app_results, tg_dp, tg_bot
from tools import send_telegram_message, get_nodes_text
from remote import monitor as remote_monitor
from telegram import operate_telegram_queue


@tg_dp.message(CommandStart())
@logger.catch
async def command_start_handler(message: Message) -> None:
    logger.debug(f"-> Enter def")
    await message.answer(f"Hello, {message.from_user.full_name}!")


@tg_dp.message()
@logger.catch
async def echo_handler(message: types.Message) -> None:
    logger.debug(f"-> Enter def")

    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Nice try!")


@logger.catch
async def main() -> None:
    logger.debug(f"-> Enter def")

    await send_telegram_message(message_text=f"🔆  Service successfully started to watch the following nodes:\n\n<pre>{await get_nodes_text()}</pre>\n\n❓  Use /help to learn how to manage settings.\n\n🐌  Main loop delay: <b>{app_config['service']['loop_timeout_sec']}</b> seconds\n📶  Probe timeout: <b>{app_config['service']['http_probe_timeout_sec']}</b> seconds")

    aio_loop = asyncio.get_event_loop()
    aio_loop.create_task(operate_telegram_queue())
    aio_loop.create_task(remote_monitor())

    await tg_dp.start_polling(tg_bot)




if __name__ == "__main__":
    logger.info(f"*** MASSA Acheta starting service...")

    for node_name in app_results:
        app_results[node_name]['last_status'] = "unknown"
        app_results[node_name]['last_update'] = 0
        app_results[node_name]['last_result'] = {}

        for wallet_addr in app_results[node_name]['wallets']:
            app_results[node_name]['wallets'][wallet_addr] = {}
            app_results[node_name]['wallets'][wallet_addr]['final_balance'] = 0
            app_results[node_name]['wallets'][wallet_addr]['candidate_rolls'] = 0
            app_results[node_name]['wallets'][wallet_addr]['active_rolls'] = 0
            app_results[node_name]['wallets'][wallet_addr]['missed_blocks'] = 0
            app_results[node_name]['wallets'][wallet_addr]['last_status'] = "unknown"
            app_results[node_name]['wallets'][wallet_addr]['last_update'] = 0
            app_results[node_name]['wallets'][wallet_addr]['last_result'] = {}

    logger.debug(f"Results file loaded successfully:\n {json.dumps(obj=app_results, indent=4)}")
    logger.info(f"Watching nodes with {app_config['service']['loop_timeout_sec']} seconds loop delay and {app_config['service']['http_probe_timeout_sec']} seconds probe timeout.")
    logger.info(f"*** Service successfully started!")

    asyncio.run(main())
