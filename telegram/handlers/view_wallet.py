from loguru import logger

from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.formatting import as_list, as_line, TextLink, Code
from aiogram.enums import ParseMode

from app_config import app_config
import app_globals

from telegram.keyboards.kb_nodes import kb_nodes
from telegram.keyboards.kb_wallets import kb_wallets
from tools import get_short_address, get_last_seen, check_privacy, get_rewards_mas_day


class WalletViewer(StatesGroup):
    waiting_node_name = State()
    waiting_wallet_address = State()

router = Router()


@router.message(StateFilter(None), Command("view_wallet"))
@logger.catch
async def cmd_view_wallet(message: Message, state: FSMContext) -> None:
    logger.debug("->Enter Def")
    logger.info(f"-> Got '{message.text}' command from '{message.from_user.id}'@'{message.chat.id}'")
    if not await check_privacy(message=message): return
    
    if len(app_globals.app_results) == 0:
        t = as_list(
            "⭕ Node list is empty", "",
            "👉 Try /help to learn how to add a node to bot"
        )
        try:
            await message.reply(
                text=t.as_html(),
                parse_mode=ParseMode.HTML,
                request_timeout=app_config['telegram']['sending_timeout_sec']
            )
        except BaseException as E:
            logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

        await state.clear()
        return


    t = as_list(
        "❓ Tap the node to select or /cancel to quit the scenario",
    )
    try:
        await state.set_state(WalletViewer.waiting_node_name)
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            reply_markup=kb_nodes(),
            request_timeout=app_config['telegram']['sending_timeout_sec']
        )
    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")
        await state.clear()

    return



@router.message(WalletViewer.waiting_node_name, F.text)
@logger.catch
async def select_wallet_to_show(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from '{message.from_user.id}'@'{message.chat.id}'")
    if not await check_privacy(message=message): return

    node_name = message.text
    if node_name not in app_globals.app_results:
        t = as_list(
            f"‼ Error: Unknown node \"{node_name}\"", "",
            "👉 Try /view_wallet to view another wallet or /help to learn bot commands"
        )
        try:
            await message.reply(
                text=t.as_html(),
                parse_mode=ParseMode.HTML,
                reply_markup=ReplyKeyboardRemove(),
                request_timeout=app_config['telegram']['sending_timeout_sec']
            )
        except BaseException as E:
            logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

        await state.clear()
        return

    if len(app_globals.app_results[node_name]['wallets']) == 0:
        t = as_list(
            f"⭕ No wallets attached to node {node_name}", "",
            "👉 Try /add_wallet to add wallet to the node or /help to learn bot commands"
        )
        try:
            await message.reply(
                text=t.as_html(),
                parse_mode=ParseMode.HTML,
                reply_markup=ReplyKeyboardRemove(),
                request_timeout=app_config['telegram']['sending_timeout_sec']
            )
        except BaseException as E:
            logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

        await state.clear()
        return

    t = as_list(
        "❓ Tap the wallet to select or /cancel to quit the scenario:",
    )
    try:
        await state.set_state(WalletViewer.waiting_wallet_address)
        await state.set_data(data={"node_name": node_name})
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            reply_markup=kb_wallets(node_name=node_name),
            request_timeout=app_config['telegram']['sending_timeout_sec']
        )
    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")
        await state.clear()

    return



@router.message(WalletViewer.waiting_wallet_address, F.text.startswith("AU"))
@logger.catch
async def show_wallet(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from '{message.from_user.id}'@'{message.chat.id}'")
    if not await check_privacy(message=message): return

    try:
        user_state = await state.get_data()
        node_name = user_state['node_name']
        wallet_address = message.text
    except BaseException as E:
        logger.error(f"Cannot read state for user '{message.from_user.id}' from chat '{message.chat.id}' ({str(E)})")
        await state.clear()
        return

    if wallet_address not in app_globals.app_results[node_name]['wallets']:
        t = as_list(
            as_line(
                "‼ Error: Wallet ",
                TextLink(
                    await get_short_address(address=wallet_address),
                    url=f"{app_config['service']['mainnet_explorer_url']}/address/{wallet_address}"
                ),
                f" is not attached to node \"{node_name}\""
            ),
            "👉 Try /view_wallet to view another wallet or /help to learn bot commands"
        )
        try:
            await message.reply(
                text=t.as_html(),
                parse_mode=ParseMode.HTML,
                request_timeout=app_config['telegram']['sending_timeout_sec']
            )
        except BaseException as E:
            logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

        await state.clear()
        return

    wallet_last_seen = await get_last_seen(
        last_time=app_globals.app_results[node_name]['wallets'][wallet_address]['last_update']
    )
    
    node_last_seen = await get_last_seen(
        last_time=app_globals.app_results[node_name]['last_update']
    )
    
    if app_globals.app_results[node_name]['last_status'] == True:
        node_status = f"🌿 Status: Online (last seen: {node_last_seen})"
    else:
        node_status = f"☠️ Status: Offline (last seen: {node_last_seen})"

    if app_globals.app_results[node_name]['wallets'][wallet_address]['last_status'] != True:
        wallet_status = as_list(
            as_line(
                f"⁉ No actual data for wallet: ",
                TextLink(
                    await get_short_address(address=wallet_address),
                    url=f"{app_config['service']['mainnet_explorer_url']}/address/{wallet_address}"
                ),
                end=""
            ),
            as_line(
                "👁 Last successful info update: ",
                wallet_last_seen
            ),
            as_line(
                "💻 Result: ",
                Code(app_globals.app_results[node_name]['wallets'][wallet_address]['last_result'])
            ),
            as_line("⚠️ Check wallet address or node settings!"),
            f"☝ Service checks updates: every {app_config['service']['main_loop_period_min']} minutes"
        )

        t = as_list(
            f"🏠 Node: \"{node_name}\"",
            f"📍 {app_globals.app_results[node_name]['url']}",
            node_status, "",
            wallet_status
        )

    else:
        wallet_final_balance = app_globals.app_results[node_name]['wallets'][wallet_address]['final_balance']
        wallet_candidate_rolls = app_globals.app_results[node_name]['wallets'][wallet_address]['candidate_rolls']
        wallet_active_rolls = app_globals.app_results[node_name]['wallets'][wallet_address]['active_rolls']
        wallet_missed_blocks = app_globals.app_results[node_name]['wallets'][wallet_address]['missed_blocks']
        wallet_computed_rewards = await get_rewards_mas_day(rolls_number=wallet_active_rolls)
        wallet_thread = app_globals.app_results[node_name]['wallets'][wallet_address]['last_result'].get("thread", 0)

        cycles_list = []
        wallet_cycles = app_globals.app_results[node_name]['wallets'][wallet_address]['last_result'].get("cycle_infos", [])

        if len(wallet_cycles) == 0:
            cycles_list.append("🌀 Cycles info: No data")
        else:
            cycles_list.append("🌀 Cycles info ( Produced / Missed):")
            for wallet_cycle in wallet_cycles:
                cycle_num = wallet_cycle.get("cycle", 0)
                ok_count = wallet_cycle.get("ok_count", 0)
                nok_count = wallet_cycle.get("nok_count", 0)
                cycles_list.append(f" ⋅ Cycle {cycle_num}: ( {ok_count} / {nok_count} )")
        

        credit_list = []
        wallet_credits = app_globals.app_results[node_name]['wallets'][wallet_address]['last_result'].get("deferred_credits", [])

        if len(wallet_credits) == 0:
            credit_list.append("💳 Deferred credits: No data")

        else:
            credit_list.append("💳 Deferred credits: ")

            for wallet_credit in wallet_credits:
                credit_amount = round(
                    float(wallet_credit['amount']),
                    4
                )

                credit_period = int(wallet_credit['slot']['period'])
                credit_unix = 1705312800 + (credit_period * 16)
                credit_date = datetime.utcfromtimestamp(credit_unix).strftime("%b %d, %Y")

                credit_list.append(
                    f" ⋅ {credit_date}: {credit_amount:,} MAS"
                )

        t = as_list(
            f"🏠 Node: \"{node_name}\"",
            f"📍 {app_globals.app_results[node_name]['url']}",
            f"{node_status}", "",
            as_line(
                "👛 Wallet: ",
                TextLink(
                    await get_short_address(address=wallet_address),
                    url=f"{app_config['service']['mainnet_explorer_url']}/address/{wallet_address}"
                ),
                end=""
            ),
            f"👁 Info updated: {wallet_last_seen}", "",
            f"💰 Final balance: {wallet_final_balance:,} MAS",
            f"🗞 Candidate / Active rolls: {wallet_candidate_rolls:,} / {wallet_active_rolls:,}",
            f"🥊 Missed blocks: {wallet_missed_blocks}", "",
            f"🪙 Estimated earnings ≈ {wallet_computed_rewards:,} MAS / Day", "",
            "🔎 Detailed info:", "",
            as_line(f"🧵 Thread: {wallet_thread}"),
            *cycles_list, "",
            *credit_list, "",
            f"☝ Service checks updates: every {app_config['service']['main_loop_period_min']} minutes"
        )

    try:
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove(),
            request_timeout=app_config['telegram']['sending_timeout_sec']
        )
    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    await state.clear()
    return
