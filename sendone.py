import asyncio
import app_globals
from aiogram.utils.formatting import as_list, as_line, Bold, Pre, Code
from aiogram.enums import ParseMode


async def main() -> None:

    t = as_list(
    )

    await app_globals.tg_bot.send_message(
        chat_id=app_globals.bot.chat_id,
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    return


if __name__ == "__main__":
    asyncio.run(main())
