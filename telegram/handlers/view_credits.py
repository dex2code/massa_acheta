from loguru import logger

from datetime import datetime
from time import time as t_now
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.formatting import as_list, as_line, TextLink, Strikethrough, Underline, Text
from aiogram.enums import ParseMode

import app_globals
from tools import get_short_address


class CreditsViewer(StatesGroup):
    waiting_wallet_address = State()

router = Router()


@logger.catch
async def get_credits(wallet_address: str="") -> Text:
    logger.debug("-> Enter Def")

    if not wallet_address.startswith("AU"):
        return as_list(
            "‼ Wrong wallet address format (expected a string starting with AU prefix)", "",
            as_line(
                "☝ Try /view_address with ",
                Underline("AU..."),
                " wallet address or /cancel to quit the scenario"
            )
        )

    wallet_credits = app_globals.deferred_credits.get(wallet_address, None)
    if not wallet_credits or type(wallet_credits) != list or len(wallet_credits) == 0:
        return as_list(
            as_line(
                "👛 Wallet: ",
                TextLink(
                    get_short_address(wallet_address),
                    url=f"{app_globals.app_config['service']['mainnet_explorer_url']}/address/{wallet_address}"
                )
            ),
            "🙅 No deferred credits available"
        )

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

    return as_list(
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



@router.message(StateFilter(None), Command("view_credits"))
@logger.catch
async def cmd_view_credits(message: Message, state: FSMContext) -> None:
    logger.debug("->Enter Def")
    logger.info(f"-> Got '{message.text}' command from user '{message.from_user.id}' in chat '{message.chat.id}'")

    message_list = message.text.split()
    if len(message_list) < 2:
        t = as_list(
            "❓ Please answer with a wallet address you want to explore: ", "",
            as_line(
                "☝ The wallet address must start with ",
                Underline("AU"),
                " prefix"
            ),
            "👉 Use /cancel to quit the scenario"

        )
        try:
            await message.reply(
                text=t.as_html(),
                parse_mode=ParseMode.HTML,
                request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
            )
            await state.set_state(CreditsViewer.waiting_wallet_address)
        except BaseException as E:
            logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")
            await state.clear()

        return

    wallet_address = message_list[1]
    t = await get_credits(wallet_address=wallet_address)
    try:
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )
    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    await state.clear()
    return



@router.message(CreditsViewer.waiting_wallet_address, F.text.startswith("AU"))
@logger.catch
async def show_credits(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from user '{message.from_user.id}' in chat '{message.chat.id}'")

    wallet_address = message.text
    t = await get_credits(wallet_address=wallet_address)
    try:
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )
    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    await state.clear()
    return
