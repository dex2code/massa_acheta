from loguru import logger

import aiohttp
import json
from aiogram.types import Message
from aiogram.utils.formatting import as_list, as_line, TextLink
from aiogram.enums import ParseMode
from time import time
from pathlib import Path

from app_config import app_config
import app_globals


@logger.catch
async def pull_http_api(api_url: str=None,
                        api_method: str="GET",
                        api_header: object={"content-type": "application/json"},
                        api_payload: object={},
                        api_content_type: str="application/json",
                        api_root_element: str=None,
                        api_session_timeout: int=app_config['service']['http_session_timeout_sec'],
                        api_probe_timeout: int=app_config['service']['http_probe_timeout_sec']) -> object:

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
def save_app_results() -> bool:
    logger.debug(f"-> Enter Def")

    composed_results = {}

    try:
        for node_name in app_globals.app_results:
            composed_results[node_name] = {}
            composed_results[node_name]['url'] = app_globals.app_results[node_name]['url']
            composed_results[node_name]['wallets'] = {}

            for wallet_address in app_globals.app_results[node_name]['wallets']:
                composed_results[node_name]['wallets'][wallet_address] = {}

        app_results_obj = Path(app_config['service']['results_path'])
        with open(file=app_results_obj, mode="wt") as output_results:
            output_results.write(json.dumps(obj=composed_results, indent=4))
            output_results.flush()
                    
    except BaseException as E:
        logger.error(f"Cannot save app_results into '{app_results_obj}' file: ({str(E)})")
        return False
        
    else:
        logger.info(f"Successfully saved app_results into '{app_results_obj}' file!")
        return True



@logger.catch
def save_app_stat() -> bool:
    logger.debug(f"-> Enter Def")

    composed_results = {
        "app_results": {},
        "massa_network": {
            "stat": []
        }
    }

    for node_name in app_globals.app_results:
        composed_results['app_results'][node_name] = {}

        for wallet_address in app_globals.app_results[node_name]['wallets']:
            composed_results['app_results'][node_name][wallet_address] = {
                "stat": []
            }

            for measure in app_globals.app_results[node_name]['wallets'][wallet_address]['stat']:
                composed_results['app_results'][node_name][wallet_address]['stat'].append(measure)

    for measure in app_globals.massa_network['stat']:
        composed_results['massa_network']['stat'].append(measure)

    try:
        app_stat_obj = Path(app_config['service']['stat_path'])
        with open(file=app_stat_obj, mode="wt") as output_stat:
            output_stat.write(json.dumps(obj=composed_results, indent=4))
            output_stat.flush()
                    
    except BaseException as E:
        logger.error(f"Cannot save app_stat into '{app_stat_obj}' file: ({str(E)})")
        return False
        
    else:
        logger.info(f"Successfully saved app_stat into '{app_stat_obj}' file!")
        return True



@logger.catch
async def t_now() -> int:
    logger.debug("-> Enter Def")

    return int(
        time()
    )



@logger.catch
async def get_last_seen(last_time: int=0, show_days: bool=False) -> str:
    logger.debug("-> Enter Def")

    if last_time == 0:
        return "Never"
    
    current_time = await t_now()
    diff_seconds = current_time - last_time

    if show_days:
        diff_days = diff_seconds // (24 * 60 * 60)
        diff_hours = (diff_seconds - (diff_days * 24 * 60 * 60)) // (60 * 60)
        diff_mins = (diff_seconds - (diff_days * 24 * 60 * 60) - (diff_hours * 60 * 60)) // 60
        result = f"{diff_days}d {diff_hours}h {diff_mins}m"
    else:
        diff_hours = diff_seconds // (60 * 60)
        diff_mins = (diff_seconds - (diff_hours * 60 * 60)) // 60
        result = f"{diff_hours}h {diff_mins}m"

    return f"{result} ago"



@logger.catch
async def get_short_address(address: str="") -> str:
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
            request_timeout=app_config['telegram']['sending_timeout_sec']
        )

        return False



@logger.catch
async def get_rewards_mas_day(rolls_number: int=0, total_rolls: int=0) -> int:
    logger.debug("-> Enter Def")

    SEC_PER_DAY = 86_400

    t0_ms = app_globals.massa_config.get("t0", None)
    if t0_ms:
        try:
            t0_sec = int(t0_ms) / 1_000
        except BaseException:
            t0_ms = 0
            t0_sec = 0
    else:
        t0_ms = 0
        t0_sec = 0
    
    threads_num = app_globals.massa_config.get("thread_count", None)
    if threads_num:
        try:
            threads_num = int(threads_num)
        except BaseException:
            threads_num = 0
    else:
        threads_num = 0

    if t0_sec and threads_num:
        blocks_per_day = (SEC_PER_DAY / t0_sec) * threads_num
    else:
        blocks_per_day = 0

    try:
        if total_rolls == 0:
            total_rolls = app_globals.massa_network['values']['total_staked_rolls']

        if total_rolls == 0 or rolls_number == 0 or blocks_per_day == 0:
            my_reward = 0
        else:
            my_contribution = total_rolls / rolls_number
            my_blocks = blocks_per_day / my_contribution
            my_reward = my_blocks * app_globals.massa_network['values']['block_reward']
            my_reward = int(my_reward)

    except BaseException as E:
        logger.error(f"Cannot compute 'rewards_mas_day' ({str(E)})")
        my_reward = 0

    return my_reward



@logger.catch
async def get_rewards_blocks_cycle(rolls_number: int=0, total_rolls: int=0) -> float:
    logger.debug("-> Enter Def")

    threads_num = app_globals.massa_config.get("thread_count", None)
    if threads_num:
        try:
            threads_num = int(threads_num)
        except BaseException:
            threads_num = 0
    else:
        threads_num = 0

    periods_per_cycle = app_globals.massa_config.get("periods_per_cycle", None)
    if periods_per_cycle:
        try:
            blocks_per_cycle = int(periods_per_cycle) * threads_num
        except BaseException:
            periods_per_cycle = 0
            blocks_per_cycle = 0
    else:
        periods_per_cycle = 0
        blocks_per_cycle = 0
    
    try:
        if total_rolls == 0:
            total_rolls = app_globals.massa_network['values']['total_staked_rolls']

        if total_rolls == 0 or rolls_number == 0:
            my_blocks = 0.0
        else:
            my_contribution = total_rolls / rolls_number
            my_blocks = round(
                blocks_per_cycle / my_contribution,
                4
            )
    
    except BaseException as E:
        logger.error(f"Cannot compute 'rewards_blocks_cycle' ({str(E)})")
        my_blocks = 0.0

    return my_blocks



async def add_public_dir(chat_id: any, wallet_address: str="") -> bool:
    logger.debug("-> Enter Def")

    try:
        chat_id = str(chat_id)
        wallet_address = str(wallet_address)
        app_globals.public_dir[chat_id] = wallet_address
    
    except BaseException as E:
        logger.warning(f"Cannot save wallet '{wallet_address}' for user '{chat_id}' ({str(E)})")
        return False
    
    else:
        logger.info(f"Successfully saved wallet '{wallet_address}' for user '{chat_id}'")
        return True


async def get_public_dir(chat_id: any) -> str:
    logger.debug("-> Enter Def")

    public_wallet_address = None
    try:
        chat_id = str(chat_id)
        public_wallet_address = app_globals.public_dir.get(chat_id, None)

    except BaseException as E:
        logger.warning(f"Cannot get public_wallet_addres for chat_id '{chat_id}' ({str(E)})")

    if public_wallet_address:
        logger.info(f"Found wallet '{public_wallet_address}' for chat_id '{chat_id}' in public_dir")
        return str(public_wallet_address)

    else:
        logger.info(f"No wallet for chat_id '{chat_id}' in public_dir")
        return None



def save_public_dir() -> bool:
    logger.debug("-> Enter Def")

    try:
        public_dir_obj = Path(app_config['service']['public_dir_path'])
        with open(file=public_dir_obj, mode="wt") as output_public_dir:
            output_public_dir.write(json.dumps(obj=app_globals.public_dir, indent=4))
            output_public_dir.flush()
                    
    except BaseException as E:
        logger.error(f"Cannot save public_dir into '{public_dir_obj}' file: ({str(E)})")
        return False
        
    else:
        logger.info(f"Successfully saved public_dir into '{public_dir_obj}' file!")
        return True



if __name__ == "__main__":
    pass
