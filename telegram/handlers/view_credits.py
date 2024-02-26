from loguru import logger

from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.formatting import as_list, as_line, TextLink, Strikethrough, Underline, Text
from aiogram.enums import ParseMode

from app_config import app_config
import app_globals

from tools import get_short_address, t_now, get_public_dir, add_public_dir


class CreditsViewer(StatesGroup):
    waiting_wallet_address = State()

router = Router()


@logger.catch
async def get_credits(wallet_address: str="") -> Text:
    logger.debug("-> Enter Def")

    if not wallet_address.startswith("AU"):
        return (False,
                as_list(
                    "‼ Wrong wallet address format (expected a string starting with AU prefix)", "",
                    as_line(
                        "☝ Try /view_address with ",
                        Underline("AU..."),
                        " wallet address"
                    )
                )
        )

    wallet_credits = app_globals.deferred_credits.get(wallet_address, None)
    if not wallet_credits or type(wallet_credits) != list or len(wallet_credits) == 0:
        return (False,
                as_list(
                    as_line(
                        "👛 Wallet: ",
                        TextLink(
                            await get_short_address(wallet_address),
                            url=f"{app_config['service']['mainnet_explorer_url']}/address/{wallet_address}"
                        )
                    ),
                    "🙅 No deferred credits available"
                )
        )

    deferred_credits = []
    deferred_credits.append("💳 Deferred credits:")

    now_unix = int(await t_now())

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
                        " ⦙\n",
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
                        " ⦙\n",
                        " ⦙… ",
                        f"{credit_date}: {credit_amount:,} MAS",
                        end=""
                    )
                )

    return (True,
            as_list(
                as_line(
                    "👛 Wallet: ",
                    TextLink(
                        await get_short_address(wallet_address),
                        url=f"{app_config['service']['mainnet_explorer_url']}/address/{wallet_address}"
                    )
                ),
                *deferred_credits, "",
                as_line(
                    "☝️ Info collected from ",
                    TextLink(
                        "MASSA repository",
                        url="https://github.com/Massa-Foundation"
                    )
                )
            )
    )



@router.message(StateFilter(None), Command("view_credits"))
@logger.catch
async def cmd_view_credits(message: Message, state: FSMContext) -> None:
    logger.debug("->Enter Def")
    logger.info(f"-> Got '{message.text}' command from '{message.from_user.id}'@'{message.chat.id}'")

    message_list = message.text.split()
    if len(message_list) < 2:

        public_wallet_address = await get_public_dir(chat_id=message.chat.id)
        if public_wallet_address:
            _, t = await get_credits(wallet_address=public_wallet_address)

        else:
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
            if not public_wallet_address:
                await state.set_state(CreditsViewer.waiting_wallet_address)

            await message.reply(
                text=t.as_html(),
                parse_mode=ParseMode.HTML,
                request_timeout=app_config['telegram']['sending_timeout_sec']
            )
        except BaseException as E:
            logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")
            await state.clear()

        return

    wallet_address = message_list[1]
    r, t = await get_credits(wallet_address=wallet_address)
    try:
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_config['telegram']['sending_timeout_sec']
        )

    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    else:
        if r:
            await add_public_dir(chat_id=message.chat.id, wallet_address=wallet_address)

    await state.clear()
    return



@router.message(CreditsViewer.waiting_wallet_address, F.text)
@logger.catch
async def show_credits(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from '{message.from_user.id}'@'{message.chat.id}'")

    wallet_address = ""
    command_list = message.text.split()
    for cmd in command_list:
        if cmd.startswith("AU"):
            wallet_address = cmd
            break

    r, t = await get_credits(wallet_address=wallet_address)
    try:
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_config['telegram']['sending_timeout_sec']
        )

    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    else:
        if r:
            await add_public_dir(chat_id=message.chat.id, wallet_address=wallet_address)

    await state.clear()
    return
