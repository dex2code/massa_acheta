from loguru import logger
logger.add("main.log", format="\"{time}\", \"{level}\", \"{file}:{line}\", \"{module}:{function}\", \"{message}\"", level="INFO", rotation="1 week", compression="zip")

import asyncio
import json
from aiogram import types as tg_types
from aiogram.filters import Command
from aiogram import html


from app_globals import app_config, app_results, tg_dp, tg_bot
from tg_queue import send_telegram_message, operate_telegram_queue
from remotes.heartbeat import heartbeat as remote_heartbeat
from remotes.release import release as remote_release
from remotes.monitor import monitor as remote_monitor


@tg_dp.message(Command("view_node"))
@logger.catch
async def view_node_handler(message: tg_types.Message) -> None:
    logger.debug(f"-> Enter Def")

    if message.chat.id != app_config['telegram']['chat_id']: return

    node_keyboard_list = [[]]

    for node_name in app_results:
        node_keyboard_list[0].append(tg_types.KeyboardButton(text=node_name))
    
    node_keyboard = tg_types.ReplyKeyboardMarkup(
        keyboard=node_keyboard_list,
        resize_keyboard=True,
        input_field_placeholder="Tap node"
        )

    await message.answer(f"Please select node:", reply_markup=node_keyboard)


@logger.catch
async def main() -> None:
    logger.debug(f"-> Enter Def")

    nodes_list = ""
    for node_name in app_results:
        node_url = app_results[node_name]['url']
        node_num_wallets = len(app_results[node_name]['wallets'])
        nodes_list += f" • {html.quote(node_name)}: {html.quote(node_url)} - {node_num_wallets} wallet(s)\n"

    if nodes_list == "": nodes_list = "⭕  Node list is empty."

    await send_telegram_message(
        message_text=f"🔆 Service successfully started to watch the following nodes:\n\n<pre>{nodes_list}</pre>\n\n❓ Use /help to learn how to manage settings.\n\n⏳ Main loop period: <b>{app_config['service']['main_loop_period_sec']}</b> seconds\n⚡ Probe timeout: <b>{app_config['service']['http_probe_timeout_sec']}</b> seconds"
    )

    aio_loop = asyncio.get_event_loop()
    aio_loop.create_task(operate_telegram_queue())
    aio_loop.create_task(remote_monitor())
    aio_loop.create_task(remote_heartbeat())
    aio_loop.create_task(remote_release())

    await tg_bot.delete_webhook(drop_pending_updates=True)
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
    logger.info(f"Watching nodes with {app_config['service']['main_loop_period_sec']} seconds loop period and {app_config['service']['http_probe_timeout_sec']} seconds probe timeout.")
    logger.info(f"*** Service successfully started!")

    asyncio.run(main())
