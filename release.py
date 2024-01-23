from loguru import logger

from app_init import current_massa_release
from tools import get_latest_massa_release, send_telegram_message


@logger.catch
async def check_release() -> None:
    logger.debug(f"-> Enter Def")

    global current_massa_release

    try:
        release_result = await get_latest_massa_release()
        latest_release = release_result['result']

    except Exception as E:
        logger.warning(f"Cannot get latest MASSA release version: ({str(E)}). Result: {release_result}")

    else:
        logger.info(f"Got latest MASSA release version: {latest_release}")

        if latest_release != current_massa_release:
            await send_telegram_message(message_text=f"📩 New MASSA release available:\n\n<pre>{current_massa_release} → {latest_release}</pre>")
        
        current_massa_release = latest_release

    return




if __name__ == "__main__":
    pass
