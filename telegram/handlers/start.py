from loguru import logger

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.utils.formatting import as_list, as_line, TextLink
from aiogram.enums import ParseMode

from app_config import app_config
import app_globals


router = Router()


@router.message(StateFilter(None), Command("start", "help"))
@logger.catch
async def cmd_start(message: Message) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from '{message.from_user.id}'@'{message.chat.id}'")

    if message.chat.id != app_globals.bot.ACHETA_CHAT:
        t = as_list(
            "📖 Commands:",
            "⦙",
            "⦙… /start or /help : This message",
            "⦙",
            "⦙… /view_address : View any wallet info",
            "⦙",
            "⦙… /clean_address : Clean your remembered address",
            "⦙",
            "⦙… /view_credits : View any wallet credits",
            "⦙",
            "⦙… /view_earnings : View earnings for Rolls number",
            "⦙",
            "⦙… /massa_info : Show MASSA network info",
            "⦙",
            "⦙… /massa_chart : Show MASSA network chart",
            "⦙",
            "⦙… /view_id : Show your TG ID",
            "⦙",
            "⦙… /cancel : Cancel ongoing scenario", "",
            as_line(
                "👉 ",
                TextLink(
                    "More info here",
                    url="https://github.com/dex2code/massa_acheta/"
                )
            ),
            as_line(
                "🎁 Wanna thank the author? ",
                TextLink(
                    "Ask me how",
                    url="https://github.com/dex2code/massa_acheta#thank-you"
                )
            )
        )

    else:
        t = as_list(
            "📖 Commands:",
            "⦙",
            "⦙… /start or /help : This message",
            "⦙",
            "⦙… /view_config : View service config",
            "⦙",
            "⦙… /view_node : View node status",
            "⦙",
            "⦙… /view_wallet : View wallet info",
            "⦙",
            "⦙… /chart_wallet : View wallet chart",
            "⦙",
            "⦙… /view_address : View any wallet info",
            "⦙",
            "⦙… /clean_address : Clean your remembered address",
            "⦙",
            "⦙… /view_credits : View any wallet credits",
            "⦙",
            "⦙… /view_earnings : View earnings for Rolls number",
            "⦙",
            "⦙… /add_node : Add node to bot",
            "⦙",
            "⦙… /add_wallet : Add wallet to bot",
            "⦙",
            "⦙… /delete_node : Delete node from bot",
            "⦙",
            "⦙… /delete_wallet : Delete wallet from bot",
            "⦙",
            "⦙… /massa_info : MASSA network info",
            "⦙",
            "⦙… /massa_chart : Show MASSA network chart",
            "⦙",
            "⦙… /acheta_release : Actual Acheta release",
            "⦙",
            "⦙… /view_id : Show your TG ID",
            "⦙",
            "⦙… /cancel : Cancel ongoing scenario",
            "⦙",
            "⦙… /reset : Reset configuration", "",
            as_line(
                "👉 ",
                TextLink(
                    "More info here",
                    url="https://github.com/dex2code/massa_acheta/"
                )
            ),
            as_line(
                "🎁 Wanna thank the author? ",
                TextLink(
                    "Ask me how",
                    url="https://github.com/dex2code/massa_acheta#thank-you"
                )
            )
        )

    try:
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_config['telegram']['sending_timeout_sec']
        )
    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    return
