from loguru import logger

import json
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.formatting import as_list, as_line, TextLink
from aiogram.enums import ParseMode

import app_globals
from tools import get_short_address


class CreditViewer(StatesGroup):
    waiting_address = State()


router = Router()


@router.message(StateFilter(None), Command("view_credits"))
@logger.catch
async def cmd_view_credits(message: Message, state: FSMContext) -> None:
    logger.debug("->Enter Def")
    logger.info(f"-> Got '{message.text}' command from user '{message.chat.id}'")

    t = as_list(
        "❓ Please enter MASSA wallet address with leading \"AU...\" prefix: ",
    )
    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    await state.set_state(CreditViewer.waiting_address)
    return



@router.message(CreditViewer.waiting_address, F.text.startswith("AU"))
@logger.catch
async def show_credits(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from user '{message.chat.id}'")

    wallet_address = message.text
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
        await message.answer(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )

        await state.clear()
        return

    deferred_credits = []
    deferred_credits.append("💳 Deferred credits:")
    deferred_credits.append(" ⦙")

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
            deferred_credits.append(
                f" ⦙…  {credit_date}: {credit_amount:,} MAS"
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
    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove(),
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    await state.clear()
    return
