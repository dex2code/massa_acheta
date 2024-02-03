from loguru import logger

import asyncio
import aiohttp
from aiogram.utils.formatting import as_list, as_line, Code, TextLink

import app_globals
from telegram.queue import queue_telegram_message


@logger.catch
async def get_latest_release_github(
    api_url: str="",
    api_content_type: str=None,
    api_session_timeout: int=app_globals.app_config['service']['http_session_timeout_sec'],
    api_probe_timeout: int=app_globals.app_config['service']['http_probe_timeout_sec']) -> object:
    logger.debug("-> Enter Def")

    api_session_timeout = aiohttp.ClientTimeout(total=api_session_timeout)
    api_probe_timeout = aiohttp.ClientTimeout(total=api_probe_timeout)

    try:
        async with aiohttp.ClientSession(timeout=api_session_timeout) as session:
            async with session.get(url=api_url, timeout=api_probe_timeout) as response:
                response_result = await response.json(content_type=api_content_type)
        response_result = {"result": response_result['name']}
        
    except Exception as E:
        logger.error(f"API request Exception: ({str(E)})")
        response_result = {"error": f"Exception: ({str(E)})"}

    else:
        if response.status != 200:
            logger.error(f"API request HTTP error: (HTTP {response.status})")
            response_result = {"error": f"HTTP ({response.status})"}
    
    finally:
        return response_result



@logger.catch
async def massa_release() -> None:
    logger.debug(f"-> Enter Def")

    try:
        massa_release_obj = await get_latest_release_github(api_url=app_globals.app_config['service']['massa_release_url'])
        massa_latest_release = massa_release_obj['result']

    except Exception as E:
        logger.warning(f"Cannot get latest MASSA release version: ({str(E)}). Result: {massa_release_obj}")

    else:
        logger.info(f"Got latest MASSA release version: '{massa_latest_release}' (current is: '{app_globals.latest_massa_release}')")

        if app_globals.latest_massa_release == "":
            pass

        elif app_globals.latest_massa_release != massa_latest_release:
            t = as_list(
                    as_line(
                        "💾 New MASSA version released: ",
                        Code(massa_latest_release)
                        ),
                    as_line("⚠ Check your nodes and update it if needed!")
                )
            await queue_telegram_message(message_text=t.as_html())
        
        app_globals.latest_massa_release = massa_latest_release



@logger.catch
async def acheta_release() -> None:
    logger.debug(f"-> Enter Def")

    try:
        acheta_release_obj = await get_latest_release_github(api_url=app_globals.app_config['service']['acheta_release_url'])
        acheta_latest_release = acheta_release_obj['result']
    
    except Exception as E:
        logger.warning(f"Cannot get latest ACHETA release version: ({str(E)}). Result: {acheta_release_obj}")
    
    else:
        logger.info(f"Got latest ACHETA release version: '{acheta_latest_release}' (local is: '{app_globals.local_acheta_release}')")

        if app_globals.latest_acheta_release == "":
            app_globals.latest_acheta_release = app_globals.local_acheta_release
        
        if app_globals.latest_acheta_release != acheta_latest_release:
            t = as_list(
                    as_line(
                        "🦗 New ACHETA version released: ",
                        Code(acheta_latest_release)
                    ),
                    as_line(
                        "💾 You have version: ",
                        Code(app_globals.local_acheta_release)
                    ),
                    as_line(
                        "⚠ Update your bot version - ",
                        TextLink(
                            "More info here",
                            url="https://github.com/dex2code/massa_acheta/"
                        )
                    )
                )
            await queue_telegram_message(message_text=t.as_html())

            app_globals.latest_acheta_release = acheta_latest_release

    return


@logger.catch
async def releases() -> None:
    logger.debug(f"-> Enter Def")

    while True:

        await massa_release()
        await acheta_release()

        await asyncio.sleep(delay=app_globals.app_config['service']['main_loop_period_sec'])




if __name__ == "__main__":
    pass
