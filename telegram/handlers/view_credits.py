from loguru import logger

from datetime import datetime
from time import time as t_now
from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.utils.formatting import as_list, as_line, TextLink, Strikethrough, Underline
from aiogram.enums import ParseMode

import app_globals
from tools import get_short_address


router = Router()


@router.message(StateFilter(None), Command("view_credits"))
@logger.catch
async def cmd_view_credits(message: Message) -> None:
    logger.debug("->Enter Def")
    logger.info(f"-> Got '{message.text}' command from user '{message.from_user.id}' in chat '{message.chat.id}'")

    message_list = message.text.split()

    if len(message_list) < 2:
        t = as_list(
            "❓ No wallet address defined", "",
            as_line(
                "☝ Try /view_credits ",
                Underline("AU..."),
                " command"
            )
        )
        try:
            await message.reply(
                text=t.as_html(),
                parse_mode=ParseMode.HTML,
                request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
            )
        except BaseException as E:
            logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

        return
    
    wallet_address = message_list[1]

    if not wallet_address.startswith("AU"):
        t = as_list(
            "‼ Wrong wallet address format", "",
            as_line(
                "☝ Try /view_credits ",
                Underline("AU..."),
                " command"
            )
        )
        try:
            await message.reply(
                text=t.as_html(),
                parse_mode=ParseMode.HTML,
                request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
            )
        except BaseException as E:
            logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

        return

    wallet_credits = app_globals.deferred_credits.get(wallet_address, None)

    if not wallet_credits or type(wallet_credits) != list or len(wallet_credits) == 0:
        t = as_list(
            as_line(
                "👛 Wallet: ",
                TextLink(
                    get_short_address(wallet_address),
                    url=f"{app_globals.app_config['service']['mainnet_explorer_url']}/address/{wallet_address}"
                )
            ),
            "🙅 No deferred credits available"
        )
        try:
            await message.reply(
                text=t.as_html(),
                parse_mode=ParseMode.HTML,
                request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
            )
        except BaseException as E:
            logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

        return

    deferred_credits = []
    deferred_credits.append("💳 Deferred credits:")
    deferred_credits.append(" ⦙")

    now_unix = int(t_now())

    for wallet_credit in wallet_credits:
        try:
            credit_amount = wallet_credit.get("amount", 0)
            credit_amount = float(credit_amount)
            credit_amount = round(credit_amount, 4)

            credit_slot = wallet_credit.get("slot", None)
            if credit_slot:
                credit_period = credit_slot.get("period", None)
                credit_period = int(credit_period)
            
            if credit_period:
                credit_unix = 1705312800 + (credit_period * 16)
                credit_date = datetime.utcfromtimestamp(credit_unix).strftime("%b %d, %Y")

        except BaseException as E:
            logger.warning(f"Cannot compute deferred credit ({str(E)}) for credit '{wallet_credit}'")
        
        else:
            if credit_unix < now_unix:
                deferred_credits.append(
                    as_line(
                        " ⦙… ",
                        Strikethrough(
                            f"{credit_date}: {credit_amount:,} MAS"
                        ),
                        end=""
                    )
                )
            else:
                deferred_credits.append(
                    as_line(
                        " ⦙… ",
                        f"{credit_date}: {credit_amount:,} MAS",
                        end=""
                    )
                )

            deferred_credits.append(" ⦙")

    deferred_credits[-1] = ""

    t = as_list(
        as_line(
            "👛 Wallet: ",
            TextLink(
                get_short_address(wallet_address),
                url=f"{app_globals.app_config['service']['mainnet_explorer_url']}/address/{wallet_address}"
            )
        ),
        *deferred_credits,
        as_line(
            "☝️ Info collected from ",
            TextLink(
                "MASSA repository",
                url="https://github.com/Massa-Foundation"
            )
        )
    )
    try:
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove(),
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )
    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    return
