from loguru import logger

import aiohttp
import json
from aiofiles import open as aiof_open

from app_globals import app_config, app_results, results_obj


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
