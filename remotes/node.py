from loguru import logger

import json
from time import time as t_now
from aiogram.utils.formatting import as_list, as_line, Code

import app_globals
from telegram.queue import queue_telegram_message
from tools import pull_node_api


@logger.catch
async def check_node(node_name: str="") -> None:
    logger.debug(f"-> Enter Def")

    payload =   json.dumps(
                    {
                        "id": 0,
                        "jsonrpc": "2.0",
                        "method": "get_status",
                        "params": []
                    }
                )

    try:
        node_result = await pull_node_api(api_url=app_globals.app_results[node_name]['url'], api_payload=payload)

        node_chain_id = node_result.get("chain_id", "")
        if node_chain_id == "":
            raise Exception(f"No chain_id in MASSA API answer: {str(node_result)}")

        node_chain_id = int(node_chain_id)

    except BaseException as E:
        logger.warning(f"Node '{node_name}' ({app_globals.app_results[node_name]['url']}) seems dead! ({str(E)})")

        if app_globals.app_results[node_name]['last_status'] != False:
            t = as_list(
                    as_line(
                        "🏠 Node: ",
                        Code(node_name),
                        end=""
                    ),
                    f"📍 {app_globals.app_results[node_name]['url']}", "",
                    "☠ Seems dead or unavailable", "",
                    as_line(
                        "💻 Result: ",
                        Code(node_result)
                    ),
                    as_line(
                        "💥 Exception: ",
                        Code(str(E))
                    ),
                    "⚠️ Check node or firewall settings!"
                )
            await queue_telegram_message(message_text=t.as_html())

        app_globals.app_results[node_name]['last_status'] = False
        app_globals.app_results[node_name]['last_result'] = node_result

    else:
        logger.info(f"Node '{node_name}' ({app_globals.app_results[node_name]['url']}) seems online ({node_chain_id=})")

        if app_globals.app_results[node_name]['last_status'] != True:
            t = as_list(
                    as_line(
                        "🏠 Node: ",
                        Code(node_name),
                        end=""
                    ),
                    f"📍 {app_globals.app_results[node_name]['url']}", "",
                    f"🌿 Become alive with Chain ID: {node_chain_id}"
                )
            await queue_telegram_message(message_text=t.as_html())

        app_globals.app_results[node_name]['last_status'] = True
        app_globals.app_results[node_name]['last_update'] = t_now()
        app_globals.app_results[node_name]['last_result'] = node_result

    finally:
        logger.debug(f"API result for node '{node_name}' ({app_globals.app_results[node_name]['url']}):\n{json.dumps(obj=app_globals.app_results[node_name]['last_result'], indent=4)}")
    
    return




if __name__ == "__main__":
    pass
