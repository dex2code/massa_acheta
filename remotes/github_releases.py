from loguru import logger

import asyncio
import aiohttp
from aiogram.utils.formatting import as_list, as_line, Code

import app_globals
from telegram.queue import queue_telegram_message


@logger.catch
async def get_latest_github_release(
    github_api_url: str="",
    api_session_timeout: int=app_globals.app_config['service']['http_session_timeout_sec'],
    api_probe_timeout: int=app_globals.app_config['service']['http_probe_timeout_sec']) -> object:
    logger.debug("-> Enter Def")

    api_session_timeout = aiohttp.ClientTimeout(total=api_session_timeout)
    api_probe_timeout = aiohttp.ClientTimeout(total=api_probe_timeout)

    try:
        async with aiohttp.ClientSession(timeout=api_session_timeout) as session:
            async with session.get(url=github_api_url, timeout=api_probe_timeout) as github_response:
                github_response_obj = await github_response.json()
        
        latest_release = github_response_obj['name']
        github_response_result = {"result": f"{latest_release}"}

    except Exception as E:
        logger.error(f"Exception in Github API request: ({str(E)})")
        github_response_result = {"error": f"Exception: ({str(E)})"}

    else:
        if latest_release == "":
            logger.error(f"Got empty string as release version!")
            github_response_result = {"error": "Empty string"}

        if github_response.status != 200:
            logger.error(f"Github API HTTP error: (HTTP {github_response.status})")
            github_response_result = {"error": f"HTTP Error: ({github_response.status})"}
    
    finally:
        return github_response_result




@logger.catch
async def release() -> None:
    logger.debug(f"-> Enter Def")

    while True:

        try:
            massa_release_result = await get_latest_github_release(
                github_api_url=app_globals.app_config['service']['massa_github_api_url']
            )
            massa_latest_release = massa_release_result['result']

        except Exception as E:
            logger.warning(f"Cannot get latest MASSA release version: ({str(E)}). Result: {massa_release_result}")

        else:
            logger.info(f"Got latest MASSA release version: '{massa_latest_release}' (current is: '{app_globals.current_massa_release}')")

            if app_globals.current_massa_release == "":
                pass

            elif app_globals.current_massa_release != massa_latest_release:
                t = as_list(
                    as_line("💾 New MASSA version released:"),
                    as_line(Code(app_globals.current_massa_release), "  →  ", Code(massa_latest_release))
                )
                await queue_telegram_message(message_text=t.as_html())
            
            app_globals.current_massa_release = massa_latest_release


        await asyncio.sleep(delay=(app_globals.app_config['service']['main_loop_period_sec'] / 2))




if __name__ == "__main__":
    pass
