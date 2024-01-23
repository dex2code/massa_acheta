from loguru import logger

import asyncio
from aiogram.enums import ParseMode

from app_init import telegram_queue, tg_bot, app_config


@logger.catch
async def operate_telegram_queue() -> None:
    logger.debug("-> Enter Def")

    while True:
        await asyncio.sleep(delay=app_config['telegram']['sending_delay_sec'])

        number_unsent_messages = len(telegram_queue)
        logger.debug(f"Telegram: {number_unsent_messages} unsent message(s) in queue")
        
        if not number_unsent_messages:
            continue

        try:
            await tg_bot.send_message(chat_id=app_config['telegram']['chat_id'], text=telegram_queue[0], parse_mode=ParseMode.HTML, request_timeout=app_config['telegram']['sending_timeout_sec'])

        except Exception as E:
            logger.error(f"Could not sent telegram message to chat_id '{app_config['telegram']['chat_id']}': ({str(E)})")
        
        else:
            logger.info(f"Successfully sent message to chat_id '{app_config['telegram']['chat_id']}' ({number_unsent_messages - 1} unsent message(s) in queue)")
            telegram_queue.popleft()




if __name__ == "__main__":
    pass
