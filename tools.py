from loguru import logger

import aiohttp
import json
from aiofiles import open as aiof_open

import app_globals


@logger.catch
async def pull_node_api(
    api_url: str="",
    api_header: object={"content-type": "application/json"},
    api_payload: object={},
    api_content_type: str=None,
    api_session_timeout: int=app_globals.app_config['service']['http_session_timeout_sec'],
    api_probe_timeout: int=app_globals.app_config['service']['http_probe_timeout_sec']) -> object:
    logger.debug(f"-> Enter Def")

    api_session_timeout = aiohttp.ClientTimeout(total=api_session_timeout)
    api_probe_timeout = aiohttp.ClientTimeout(total=api_probe_timeout)

    try:
        async with aiohttp.ClientSession(timeout=api_session_timeout) as session:
            async with session.post(url=api_url, headers=api_header, data=api_payload, timeout=api_probe_timeout) as api_response:
                api_response_obj = await api_response.json(content_type=api_content_type)
        
        api_response_result = api_response_obj['result']

    except Exception as E:
        logger.error(f"Exception in API request for URL '{api_url}': ({str(E)})")
        api_response_result = {"error": f"Exception: ({str(E)})"}

    else:
        if api_response.status == 200:
            logger.info(f"Successfully pulled result from API '{api_url}'")
        else:
            logger.error(f"API URL '{api_url}' response status error: (HTTP {api_response.status})")
            api_response_result = {"error": f"HTTP Error: ({api_response.status})"}

    finally:
        return api_response_result



@logger.catch
async def save_app_results() -> bool:
    logger.debug(f"-> Enter Def")

    composed_results = {}

    for node_name in app_globals.app_results:
        composed_results[node_name] = {}
        composed_results[node_name]['url'] = app_globals.app_results[node_name]['url']
        composed_results[node_name]['wallets'] = {}

        for wallet_address in app_globals.app_results[node_name]['wallets']:
            composed_results[node_name]['wallets'][wallet_address] = {}

    try:
        async with aiof_open(app_globals.results_obj, "w") as output_results:
            await output_results.write(json.dumps(obj=composed_results, indent=4))
            await output_results.flush()
                    
    except Exception as E:
        logger.critical(f"Cannot save app_results into '{app_globals.results_obj}' file: ({str(E)})")
        return False
        
    else:
        logger.info(f"Successfully saved app_results into '{app_globals.results_obj}' file!")
        return True



@logger.catch
def get_list_nodes() -> list:
    logger.debug("-> Enter Def")

    result_list = []

    for node_name in app_globals.app_results:
        result_list.append(node_name)
    
    return result_list



@logger.catch
def get_list_wallets(node_name: str="") -> list:
    logger.debug("-> Enter Def")

    result_list = []

    if node_name not in app_globals.app_results:
        return result_list
    
    for wallet_address in app_globals.app_results[node_name]['wallets']:
        result_list.append(wallet_address)
    
    return result_list



@logger.catch
def get_all_wallets() -> list:
    logger.debug("-> Enter Def")

    result_list = []

    for node_name in app_globals.app_results:
        for wallet_address in app_globals.app_results[node_name]['wallets']:
            result_list.append(wallet_address)

    logger.info(f"{result_list=}")
    return result_list



@logger.catch
def get_last_seen(last_time: float=0.0, current_time: float=0.0) -> str:
    logger.debug("-> Enter Def")

    if last_time == 0:
        return "Never"
    
    diff_time = int(current_time - last_time)
    diff_hours = diff_time // 3600
    diff_mins = (diff_time - (diff_hours * 3600)) // 60

    return f"{diff_hours}h {diff_mins}m ago"



@logger.catch
def get_short_address(address: str="") -> str:
    logger.debug("-> Enter Def")

    if len(address) > 15:
        return f"{address[0:9]}...{address[-6:]}"
    else:
        return address




if __name__ == "__main__":
    pass
