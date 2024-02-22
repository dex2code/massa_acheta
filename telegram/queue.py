from loguru import logger

import asyncio
from aiogram.enums import ParseMode

from app_config import app_config
import app_globals


@logger.catch
async def queue_telegram_message(chat_id: str=app_globals.bot.ACHETA_CHAT, message_text: str="") -> bool:
    logger.debug(f"-> Enter Def")

    try:
        app_globals.telegram_queue.append(
            {
                "chat_id": chat_id,
                "message_text": message_text
            }
        )
    
    except BaseException as E:
        logger.error(f"Cannot add telegram message to queue : ({str(E)})")
        return False

    else:
        logger.info(f"Successfully added telegram message to queue!")
        return True



@logger.catch
async def operate_telegram_queue() -> None:
    logger.debug("-> Enter Def")

    try:
        while True:
            await asyncio.sleep(delay=app_config['telegram']['sending_delay_sec'])

            number_unsent_messages = len(app_globals.telegram_queue)
            logger.debug(f"Telegram: {number_unsent_messages} unsent message(s) in queue")
            
            if number_unsent_messages == 0:
                continue

            try:
                chat_id = app_globals.telegram_queue[0]['chat_id']
                message_text = app_globals.telegram_queue[0]['message_text']

                await app_globals.tg_bot.send_message(
                    chat_id=chat_id,
                    text=message_text,
                    parse_mode=ParseMode.HTML,
                    request_timeout=app_config['telegram']['sending_timeout_sec']
                )

            except BaseException as E:
                logger.error(f"Could not send telegram message to chat_id '{app_globals.bot.ACHETA_CHAT}': ({str(E)})")

            else:
                logger.info(f"Successfully sent message to chat_id '{app_globals.bot.ACHETA_CHAT}' ({number_unsent_messages - 1} unsent message(s) in queue)")
                app_globals.telegram_queue.popleft()

    except BaseException as E:
        logger.error(f"Exception {str(E)} ({E})")
    
    finally:
        logger.error(f"<- Quit Def")

    return




if __name__ == "__main__":
    pass
