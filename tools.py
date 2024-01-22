from loguru import logger

import aiohttp
import json
from aiofiles import open as aiof_open

from app_init import app_config, app_results, telegram_queue, results_obj


@logger.catch
async def pull_node_api(
        api_url: str="",
        api_header: object={"content-type": "application/json"},
        api_payload: object={},
        api_session_timeout: int=app_config['service']['http_session_timeout_sec'],
        api_probe_timeout: int=app_config['service']['http_probe_timeout_sec']) -> object:
    logger.debug(f"-> Enter Def")

    api_session_timeout = aiohttp.ClientTimeout(total=api_session_timeout)
    api_probe_timeout = aiohttp.ClientTimeout(total=api_probe_timeout)

    async with aiohttp.ClientSession(timeout=api_session_timeout) as session:

        try:
            async with session.post(url=api_url, headers=api_header, data=api_payload, timeout=api_probe_timeout) as api_response:
                api_response_obj = await api_response.json()
                api_response_result = api_response_obj['result']

        except Exception as E:
            logger.error(f"Exception in API request for URL '{api_url}': ({str(E)})")
            api_response_result = {"error": f"Exception: ({str(E)})"}

        else:
            if api_response.status != 200:
                logger.error(f"API URL '{api_url}' response status error: (HTTP {api_response.status})")
                api_response_result = {"error": f"HTTP Error: ({api_response.status})"}

    return api_response_result




@logger.catch
async def send_telegram_message(message_text: str="") -> None:
    logger.debug(f"-> Enter Def")

    try:
        telegram_queue.append(message_text)
    
    except Exception as E:
        logger.error(f"Cannot add telegram message to queue : ({str(E)})")

    else:
        logger.info(f"Successfully added telegram message to queue!")

    return




@logger.catch
async def get_nodes_text() -> str:
    logger.debug(f"-> Enter Def")

    nodes_list = ""
    for node_name in app_results:
        node_url = app_results[node_name]['url']
        node_num_wallets = len(app_results[node_name]['wallets'])
        nodes_list += f" • {node_name}: {node_url} - {node_num_wallets} wallet(s)\n"

    if nodes_list == "":
        return "⭕  Node list is empty."
    else:
        return nodes_list.rstrip()




@logger.catch
async def save_results() -> bool:
    logger.debug(f"-> Enter Def")

    composed_results = {}

    for node_name in app_results:
        composed_results[node_name] = {}
        composed_results[node_name]['url'] = app_results[node_name]['url']
        composed_results[node_name]['wallets'] = {}
        for wallet_address in app_results[node_name]['wallets']:
            composed_results[node_name]['wallets'][wallet_address] = {}

    async with aiof_open(results_obj, "w") as output_results:

        try:
            await output_results.write(json.dumps(obj=composed_results, indent=4))
            await output_results.flush()
                    
        except Exception as E:
            logger.critical(f"Cannot save app_results into '{results_obj}' file: ({str(E)})")
            return False
        
        else:
            logger.info(f"Successfully saved app_results into '{results_obj}' file!")
            return True




if __name__ == "__main__":
    pass
