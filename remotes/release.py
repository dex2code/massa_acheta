from loguru import logger

import asyncio
import aiohttp
from aiogram.utils.formatting import as_list, as_line, Code

from app_globals import app_config, current_massa_release
from telegram.queue import queue_telegram_message


@logger.catch
async def get_latest_massa_release(
    github_api_url: str=app_config['service']['github_api_url'],
    api_session_timeout: int=app_config['service']['http_session_timeout_sec'],
    api_probe_timeout: int=app_config['service']['http_probe_timeout_sec']) -> object:
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

    global current_massa_release

    while True:

        await asyncio.sleep(delay=(app_config['service']['main_loop_period_sec'] / 2))

        try:
            release_result = await get_latest_massa_release()
            latest_release = release_result['result']

        except Exception as E:
            logger.warning(f"Cannot get latest MASSA release version: ({str(E)}). Result: {release_result}")

        else:
            logger.info(f"Got latest MASSA release version: '{latest_release}'")

            if current_massa_release == "":
                t = as_list(
                    as_line("💾 Latest released MASSA version:"),
                    Code(latest_release)
                )
                await queue_telegram_message(message_text=t.as_html())

            elif current_massa_release != latest_release:
                t = as_list(
                    as_line("💾 New MASSA version released:"),
                    as_line(Code(current_massa_release), " → ", Code(latest_release))
                )
                await queue_telegram_message(message_text=t)
            
            current_massa_release = latest_release




if __name__ == "__main__":
    pass
