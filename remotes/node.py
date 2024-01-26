from loguru import logger

import json
from time import time as t_now
from aiogram.utils.formatting import as_list, as_line, Code

from app_globals import app_results
from telegram.queue import queue_telegram_message
from tools import pull_node_api


@logger.catch
async def check_node(node_name: str="") -> None:
    logger.debug(f"-> Enter Def")

    global app_results

    payload = json.dumps({
        "id": 0,
        "jsonrpc": "2.0",
        "method": "get_status",
        "params": []
    })

    try:
        node_result = await pull_node_api(api_url=app_results[node_name]['url'], api_payload=payload)
        node_chain_id = node_result['chain_id']
        node_chain_id = int(node_chain_id)

    except Exception as E:
        logger.warning(f"Node '{node_name}' ({app_results[node_name]['url']}) seems dead! ({str(E)})")

        if app_results[node_name]['last_status'] != False:
            t = as_list(
                as_line(f"🏠 Node: ", Code(node_name), end=""),
                f"📍 {app_results[node_name]['url']}", "",
                "☠ Seems dead or unavailable!", "",
                Code(f"💻 {node_result}"), "",
                "⚠️ Check node or firewall settings!"
            )
            await queue_telegram_message(message_text=t.as_html())

        app_results[node_name]['last_status'] = False
        app_results[node_name]['last_result'] = node_result

    else:
        logger.info(f"Node '{node_name}' ({app_results[node_name]['url']}) seems online!")

        if app_results[node_name]['last_status'] != True:
            t = as_list(
                as_line(f"🏠 Node: ", Code(node_name), end=""),
                f"📍 {app_results[node_name]['url']}", "",
                f"🌿 Become alive with Chain ID: {node_chain_id}",
            )
            await queue_telegram_message(message_text=t.as_html())

        app_results[node_name]['last_status'] = True
        app_results[node_name]['last_update'] = t_now()
        app_results[node_name]['last_result'] = node_result

    finally:
        logger.debug(f"API result for node '{node_name}' ({app_results[node_name]['url']}):\n{json.dumps(obj=app_results[node_name]['last_result'], indent=4)}")

    
    return




if __name__ == "__main__":
    pass
