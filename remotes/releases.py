from loguru import logger

from aiogram.utils.formatting import as_list, as_line, TextLink

from app_config import app_config
import app_globals

from telegram.queue import queue_telegram_message
from tools import pull_http_api


@logger.catch
async def massa_release() -> None:
    logger.debug(f"-> Enter Def")

    massa_release_answer = {"error": "No response from remote HTTP API"}
    try:
        massa_release_answer = await pull_http_api(api_url=app_config['service']['massa_release_url'],
                                                   api_method="GET",
                                                   api_root_element="name")

        massa_release_result = massa_release_answer.get("result", None)
        if not massa_release_result:
            raise Exception(f"Wrong answer from '{app_config['service']['massa_release_url']}' ({str(massa_release_answer)})")

    except BaseException as E:
        logger.warning(f"Cannot get latest MASSA release version: ({str(E)}). Result: {massa_release_answer}")

    else:
        logger.info(f"Got latest MASSA release version: '{massa_release_result}' (current is: '{app_globals.massa_network['values']['latest_release']}')")

        if app_globals.massa_network['values']['latest_release'] == "":
            pass

        elif app_globals.massa_network['values']['latest_release'] != massa_release_result:
            t = as_list(
                f"💾 A new MASSA version released: {massa_release_result}", "",
                "⚠ Check your nodes and update it if needed!"
            )
            await queue_telegram_message(message_text=t.as_html())
        
        app_globals.massa_network['values']['latest_release'] = massa_release_result

    return



@logger.catch
async def acheta_release() -> None:
    logger.debug(f"-> Enter Def")

    try:
        acheta_release_answer = await pull_http_api(api_url=app_config['service']['acheta_release_url'],
                                                   api_method="GET",
                                                   api_root_element="name")

        acheta_release_result = acheta_release_answer.get("result", None)
        if not acheta_release_result:
            raise Exception(f"Wrong answer from MASSA node API ({str(acheta_release_answer)})")
    
    except BaseException as E:
        logger.warning(f"Cannot get latest ACHETA release version: ({str(E)}). Result: {acheta_release_answer}")
    
    else:
        logger.info(f"Got latest ACHETA release version: '{acheta_release_result}' (local is: '{app_globals.local_acheta_release}')")

        if app_globals.latest_acheta_release == "":
            app_globals.latest_acheta_release = app_globals.local_acheta_release
        
        if app_globals.latest_acheta_release != acheta_release_result:
            t = as_list(
                f"🦗 A new ACHETA version released: {acheta_release_result}", "",
                f"💾 You have version: {app_globals.local_acheta_release}", "",
                as_line(
                    "⚠ Update your bot version - ",
                    TextLink(
                        "More info here",
                        url="https://github.com/dex2code/massa_acheta/"
                    )
                )
            )
            await queue_telegram_message(message_text=t.as_html())

            app_globals.latest_acheta_release = acheta_release_result

    return



@logger.catch
async def check_releases() -> None:
    logger.debug(f"-> Enter Def")

    await massa_release()
    await acheta_release()




if __name__ == "__main__":
    pass
