from loguru import logger

from time import time as t_now
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.formatting import as_list, as_line, TextLink, Code
from aiogram.enums import ParseMode

import app_globals
from telegram.keyboards.kb_nodes import kb_nodes
from telegram.keyboards.kb_wallets import kb_wallets
from tools import get_list_nodes, get_all_wallets, get_short_address, get_last_seen


class WalletViewer(StatesGroup):
    waiting_node_name = State()
    waiting_wallet_address = State()


router = Router()


@router.message(StateFilter(None), Command("view_wallet"))
@logger.catch
async def cmd_view_wallet(message: Message, state: FSMContext) -> None:
    logger.debug("->Enter Def")
    if message.chat.id != app_globals.bot.chat_id: return
    
    if len(app_globals.app_results) == 0:
        t = as_list(
                app_globals.app_config['telegram']['service_nickname'], "",
                "⭕ Node list is empty.", "",
                "❓ Try /help to learn how to add a node to bot."
            )
        await message.answer(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )

        await state.clear()
        return


    t = as_list(
            as_line(app_globals.app_config['telegram']['service_nickname']),
            "❓ Tap the node to select or /cancel to quit the scenario.",
        )
    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        reply_markup=kb_nodes(),
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    await state.set_state(WalletViewer.waiting_node_name)
    return



@router.message(WalletViewer.waiting_node_name, F.text.in_(get_list_nodes()))
@logger.catch
async def select_wallet_to_show(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    if message.chat.id != app_globals.bot.chat_id: return

    node_name = message.text
    await state.set_data(data={"node_name": node_name})

    if node_name not in app_globals.app_results:
        t = as_list(
                as_line(app_globals.app_config['telegram']['service_nickname']),
                "‼ Error. Unknown node.", "",
                "❓ Try /help to learn how to add a node to bot."
            )
        await message.answer(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove(),
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )

        await state.clear()
        return

    if len(app_globals.app_results[node_name]['wallets']) == 0:
        t = as_list(
                as_line(app_globals.app_config['telegram']['service_nickname']),
                "⭕ No wallets attached to selected node!", "",
                "❓ Try /help to learn how to add a wallet to bot."
            )
        await message.answer(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove(),
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )

        await state.clear()
        return

    t = as_list(
            as_line(app_globals.app_config['telegram']['service_nickname']),
            "❓ Tap the wallet to select or /cancel to quit the scenario.",
        )
    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        reply_markup=kb_wallets(node_name=node_name),
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    await state.set_state(WalletViewer.waiting_wallet_address)
    return



@router.message(WalletViewer.waiting_wallet_address, F.text.in_(get_all_wallets()))
@logger.catch
async def show_wallet(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    if message.chat.id != app_globals.bot.chat_id: return

    user_state = await state.get_data()
    node_name = user_state['node_name']
    wallet_address = message.text

    if wallet_address not in app_globals.app_results[node_name]['wallets']:
        t = as_list(
                as_line(app_globals.app_config['telegram']['service_nickname']),
                as_line(
                    "‼ Error. Wallet ",
                    TextLink(
                        get_short_address(address=wallet_address),
                        url=f"{app_globals.app_config['service']['mainnet_explorer']}/address/{wallet_address}"
                    ),
                    f" is not attached to node {node_name}. Try another one."
                ),
                "❓ Try /help to learn how to add a wallet to bot."
            )
        await message.answer(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )
        return

    current_time = t_now()

    wallet_last_seen =  get_last_seen(
                            last_time=app_globals.app_results[node_name]['wallets'][wallet_address]['last_update'],
                            current_time=current_time
                        )
    
    node_last_seen =    get_last_seen(
                            last_time=app_globals.app_results[node_name]['last_update'],
                            current_time=current_time
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
                                    get_short_address(address=wallet_address),
                                    url=f"{app_globals.app_config['service']['mainnet_explorer']}/address/{wallet_address}"
                                ),
                                end=""
                            ),
                            as_line(
                                "👁 Last successful data update: ",
                                wallet_last_seen
                            ),
                            as_line(
                                "💻 Result: ",
                                Code(app_globals.app_results[node_name]['wallets'][wallet_address]['last_result'])
                            ),
                            as_line("⚠️ Check wallet address or node settings!"),
                            f"⏳ Service checks updates: every {app_globals.app_config['service']['main_loop_period_sec']} seconds"
                        )

        t = as_list(
                as_line(app_globals.app_config['telegram']['service_nickname']),
                as_line(
                    "🏠 Node: ",
                    Code(node_name),
                    end=""
                ),
                f"📍 {app_globals.app_results[node_name]['url']}",
                node_status, "",
                wallet_status
            )

    else:
        wallet_final_balance = app_globals.app_results[node_name]['wallets'][wallet_address]['final_balance']
        wallet_candidate_rolls = app_globals.app_results[node_name]['wallets'][wallet_address]['candidate_rolls']
        wallet_active_rolls = app_globals.app_results[node_name]['wallets'][wallet_address]['active_rolls']
        wallet_missed_blocks = app_globals.app_results[node_name]['wallets'][wallet_address]['missed_blocks']
        wallet_thread = app_globals.app_results[node_name]['wallets'][wallet_address]['last_result'].get("thread", 0)

        cycles_list = []
        wallet_cycles = app_globals.app_results[node_name]['wallets'][wallet_address]['last_result'].get("cycle_infos", [])

        if len(wallet_cycles) == 0:
            cycles_list.append("🌀 Cycles info: No data")
        else:
            cycles_list.append("🌀 Cycles info (produced/missed blocks):")
            for wallet_cycle in wallet_cycles:
                cycle_num = wallet_cycle.get("cycle", 0)
                ok_count = wallet_cycle.get("ok_count", 0)
                nok_count = wallet_cycle.get("nok_count", 0)
                cycles_list.append(f" ⋅ Cycle {cycle_num}: {ok_count}/{nok_count}")
        

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
                credit_date = datetime.utcfromtimestamp(credit_unix).strftime("%b %d, %Y %I:%M %p UTC")

                credit_list.append(
                    as_line(
                        " ⋅ ",
                        credit_date,
                        ": ",
                        Code(credit_amount),
                        " MASSA",
                        end=""
                    )
                )

        t = as_list(
                as_line(app_globals.app_config['telegram']['service_nickname']),
                as_line(
                    "🏠 Node: ",
                    Code(node_name),
                    end=""
                ),
                f"📍 {app_globals.app_results[node_name]['url']}",
                f"{node_status}", "",
                as_line(
                    "👛 Wallet: ",
                    TextLink(
                        get_short_address(address=wallet_address),
                        url=f"{app_globals.app_config['service']['mainnet_explorer']}/address/{wallet_address}"
                    ),
                    end=""
                ),
                f"👁 Info updated: {wallet_last_seen}", "",
                f"💰 Final balance: {wallet_final_balance} MASSA",
                f"🧻 Candidate/Active rolls: {wallet_candidate_rolls}/{wallet_active_rolls}",
                f"🥊 Missed blocks: {wallet_missed_blocks}", "",
                "🔎 Detailed info:", "",
                as_line(f"🧵 Thread: {wallet_thread}"),
                *cycles_list, "",
                *credit_list, "",
                f"⏳ Service checks updates: every {app_globals.app_config['service']['main_loop_period_sec']} seconds"
            )


    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove(),
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    await state.clear()
    return
