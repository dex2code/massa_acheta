import asyncio
from app_globals import tg_bot, app_config, bot
from aiogram.utils.formatting import as_list, as_line, Bold, Pre, Code
from aiogram.enums import ParseMode


async def main():
    t = as_list(
    )

    await tg_bot.send_message(chat_id=bot.chat_id, text=t.as_html(), parse_mode=ParseMode.HTML, request_timeout=app_config['telegram']['sending_timeout_sec'])


if __name__ == "__main__":
    asyncio.run(main())
