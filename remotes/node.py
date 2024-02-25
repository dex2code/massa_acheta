from loguru import logger

import json
from aiogram.utils.formatting import as_list, as_line, Code

import app_globals

from telegram.queue import queue_telegram_message
from tools import pull_http_api, t_now


@logger.catch
async def check_node(node_name: str="") -> None:
    logger.debug(f"-> Enter Def")

    payload = json.dumps(
        {
            "id": 0,
            "jsonrpc": "2.0",
            "method": "get_status",
            "params": []
        }
    )

    node_answer = {"error": "No response from remote HTTP API"}
    try:
        node_answer = await pull_http_api(api_url=app_globals.app_results[node_name]['url'],
                                          api_method="POST",
                                          api_payload=payload,
                                          api_root_element="result")

        node_result = node_answer.get("result", None)
        if not node_result:
            raise Exception(f"Wrong answer from MASSA node API ({str(node_answer)})")

        node_chain_id = node_result.get("chain_id", None)
        if not node_chain_id:
            raise Exception(f"No 'chain_id' in MASSA node API answer")
        
        node_current_cycle = node_result.get("current_cycle", None)
        if not node_current_cycle:
            raise Exception(f"No 'current_cycle' in MASSA node API answer")

    except BaseException as E:
        logger.warning(f"Node '{node_name}' ({app_globals.app_results[node_name]['url']}) seems dead! ({str(E)})")

        if app_globals.app_results[node_name]['last_status'] != False:
            t = as_list(
                f"🏠 Node: \"{node_name}\"",
                f"📍 {app_globals.app_results[node_name]['url']}", "",
                "☠ Seems dead or unavailable", "",
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
                f"🏠 Node: \"{node_name}\"",
                f"📍 {app_globals.app_results[node_name]['url']}", "",
                f"🌿 Become alive with chain ID: {node_chain_id}",
                f"🌀 Current cycle: {node_current_cycle}"
            )
            await queue_telegram_message(message_text=t.as_html())

        else:
            # If Node Cycle number is less than MASSA Cycle number
            if node_current_cycle < app_globals.massa_network['values']['current_cycle']:
                t = as_list(
                    f"🏠 Node: \"{node_name}\"",
                    f"📍 {app_globals.app_results[node_name]['url']}", "",
                    f"🌀 Cycle number mismatch!", "",
                    f"👁 Node Cycle ID is less than expected ({node_current_cycle} < {app_globals.massa_network['values']['current_cycle']})", "",
                    "⚠️ Check node status!"
                )
                await queue_telegram_message(message_text=t.as_html())

        app_globals.app_results[node_name]['last_status'] = True
        app_globals.app_results[node_name]['last_update'] = await t_now()
        app_globals.app_results[node_name]['last_chain_id'] = node_chain_id
        app_globals.app_results[node_name]['last_cycle'] = node_current_cycle
        app_globals.app_results[node_name]['last_result'] = node_result
    
    return




if __name__ == "__main__":
    pass
