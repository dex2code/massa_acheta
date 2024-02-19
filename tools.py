from loguru import logger

import aiohttp
import json
from aiofiles import open as aiof_open
from aiogram.types import Message
from aiogram.utils.formatting import as_list, as_line, TextLink
from aiogram.enums import ParseMode

import app_globals


@logger.catch
async def pull_http_api(api_url: str=None,
                        api_method: str="GET",
                        api_header: object={"content-type": "application/json"},
                        api_payload: object={},
                        api_content_type: str="application/json",
                        api_root_element: str=None,
                        api_session_timeout: int=app_globals.app_config['service']['http_session_timeout_sec'],
                        api_probe_timeout: int=app_globals.app_config['service']['http_probe_timeout_sec']) -> object:

    logger.debug(f"-> Enter Def")

    api_session_timeout = aiohttp.ClientTimeout(total=api_session_timeout)
    api_probe_timeout = aiohttp.ClientTimeout(total=api_probe_timeout)

    api_response_text = "No response from remote HTTP API"
    api_response_obj = {"error": "No response from remote HTTP API"}

    try:
        async with aiohttp.ClientSession(timeout=api_session_timeout) as session:

            if api_method == "GET":
                async with session.get(url=api_url, headers=api_header, timeout=api_probe_timeout) as api_response:
                    if api_response.status != 200:
                        raise Exception(f"Remote HTTP API Error '{str(api_response.status)}'")
                    if api_response.content_type != api_content_type:
                        raise Exception(f"Remote HTTP API wrong content type '{str(api_response.content_type)}'")
                    api_response_text = await api_response.text()

            elif api_method == "POST":
                async with session.post(url=api_url, headers=api_header, data=api_payload, timeout=api_probe_timeout) as api_response:
                    if api_response.status != 200:
                        raise Exception(f"Remote HTTP API Error '{str(api_response.status)}'")
                    if api_response.content_type != api_content_type:
                        raise Exception(f"Remote API wrong content type '{str(api_response.content_type)}'")
                    api_response_text = await api_response.text()

            else:
                raise Exception(f"Unknown HTTP API method '{api_method}'")


        if api_content_type == "application/json":
            api_response_obj = json.loads(s=api_response_text)

            if not api_root_element:
                api_result = {"result": api_response_obj}
            else:
                api_result = api_response_obj.get(api_root_element, None)
                if not api_result:
                    raise Exception(f"A mandatory key '{api_root_element}' missed in remote HTTP API response: {api_response_text}")
                else:
                    api_result = {"result": api_result}
        else:
            api_result = {"result": api_response_text}

    except BaseException as E:
        logger.error(f"Exception in remote HTTP API request for URL '{api_url}': ({str(E)})")
        api_result = {"error": str(E)}

    else:
        logger.info(f"Successfully pulled from remote HTTP API '{api_url}'")

    finally:
        return api_result



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
                    
    except BaseException as E:
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

    if len(address) > 16:
        return f"{address[0:8]}...{address[-6:]}"
    else:
        return address



@logger.catch
async def check_privacy(message: Message) -> bool:
    logger.debug("-> Enter Def")

    if message.chat.id == app_globals.bot.ACHETA_CHAT:
        return True
    
    else:
        t = as_list(
            "🔑 This is a private telegram bot with limited public availability", "",
            "MASSA 🦗 Acheta is not a public service but opensource software that you can install on your own server",
            as_line(
                "👉 ",
                TextLink(
                    "More info here",
                    url="https://github.com/dex2code/massa_acheta"
                )
            ),
            "☝ Try /help to get a list of public commands"
        )
        await message.answer(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )

        return False



@logger.catch
async def get_rewards(rolls_number: int=0) -> int:
    logger.debug("-> Enter Def")

    if app_globals.massa_network['values']['total_staked_rolls'] == 0 or rolls_number == 0 or app_globals.massa_network['values']['block_reward'] == 0:
        my_reward = 0

    else:
        my_contribution = app_globals.massa_network['values']['total_staked_rolls'] / rolls_number
        my_blocks = 172_800 / my_contribution
        my_reward = my_blocks * app_globals.massa_network['values']['block_reward']
        my_reward = int(my_reward)

    return my_reward




if __name__ == "__main__":
    pass
