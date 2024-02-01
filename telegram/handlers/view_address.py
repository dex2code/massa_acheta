from loguru import logger

import json
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.formatting import as_list, as_line, Code, TextLink
from aiogram.enums import ParseMode

import app_globals
from tools import get_short_address, pull_node_api


class AddressViewer(StatesGroup):
    waiting_address = State()


router = Router()


@router.message(StateFilter(None), Command("view_address"))
@logger.catch
async def cmd_view_address(message: Message, state: FSMContext) -> None:
    logger.debug("->Enter Def")
    if message.chat.id != app_globals.bot.chat_id: return
    
    t = as_list(
            as_line(app_globals.app_config['telegram']['service_nickname']),
            "❓ Please enter MASSA wallet address with leading AU... prefix:",
        )
    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    await state.set_state(AddressViewer.waiting_address)
    return



@router.message(AddressViewer.waiting_address, F.text.startswith('AU'))
@logger.catch
async def show_address(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    if message.chat.id != app_globals.bot.chat_id: return

    wallet_address = message.text

    t = as_list(
            as_line(app_globals.app_config['telegram']['service_nickname']),
            as_line(
                "🕑 Trying to collect info for wallet: ",
                TextLink(
                    get_short_address(wallet_address),
                    url=f"{app_globals.app_config['service']['mainnet_explorer']}/address/{wallet_address}"
                ),
                end=""
            ),
            "This may take some time, info will be displayed here as soon as we receive the answer from Mainnet RPC..."
        )

    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove(),
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )


    payload =   json.dumps(
                    {
                        "id": 0,
                        "jsonrpc": "2.0",
                        "method": "get_addresses",
                        "params": [[wallet_address]]
                    }
                )

    try:
        wallet_response =   await pull_node_api(
                                api_url=app_globals.app_config['service']['mainnet_rpc'],
                                api_payload=payload
                            )
        
        if type(wallet_response) != list or not len(wallet_response) or "address" not in wallet_response[0]:
            raise KeyError(wallet_response)

        wallet_result = wallet_response[0]
        wallet_result_address = wallet_result.get("address", "None")
        if wallet_result_address != wallet_address:
            raise ValueError(
                {
                    "error": f"Wrong address received from Mainnet RPC: '{wallet_result_address}'"
                }
            )
    
    except Exception as E:
        logger.warning(f"Cannot operate received address result: ({str(E)})")

        t = as_list(
                as_line(app_globals.app_config['telegram']['service_nickname']),
                as_line(
                    "👛 Wallet: ",
                    TextLink(
                        get_short_address(wallet_address),
                        url=f"{app_globals.app_config['service']['mainnet_explorer']}/address/{wallet_address}"
                    )
                ),
                as_line(
                    "⁉ Error getting address info for wallet: ",
                    TextLink(
                        get_short_address(wallet_address),
                        url=f"{app_globals.app_config['service']['mainnet_explorer']}/address/{wallet_address}"
                    )
                ),
                as_line(
                    "💻 Result: ",
                    Code(str(E))
                ),
                as_line("⚠️ Check wallet address or try later!")
            )
        await message.answer(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )

    else:
        logger.info(f"Successfully received result for address '{wallet_address}'")

        wallet_final_balance = 0
        wallet_final_balance = wallet_result.get("final_balance", 0)
        wallet_final_balance = float(wallet_final_balance)
        wallet_final_balance = round(wallet_final_balance, 4)

        wallet_candidate_rolls = 0
        wallet_candidate_rolls = wallet_result.get("candidate_roll_count", 0)
        wallet_candidate_rolls = int(wallet_candidate_rolls)

        wallet_active_rolls = 0
        if type(wallet_result['cycle_infos'][-1].get("active_rolls", 0)) == int:
            wallet_active_rolls = wallet_result['cycle_infos'][-1].get("active_rolls", 0)

        wallet_missed_blocks = 0
        for cycle_info in wallet_result.get("cycle_infos", []):
            if type(cycle_info.get("nok_count", 0)) == int:
                wallet_missed_blocks += cycle_info.get("nok_count", 0)

        wallet_thread = wallet_result.get("thread", 0)

        cycles_list = []
        wallet_cycles = wallet_result.get("cycle_infos", [])

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
        wallet_credits = wallet_result.get("deferred_credits", [])

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
                    "👛 Wallet: ",
                    TextLink(
                        get_short_address(wallet_address),
                        url=f"{app_globals.app_config['service']['mainnet_explorer']}/address/{wallet_address}"
                    )
                ),
                f"💰 Final balance: {wallet_final_balance} MASSA",
                f"🧻 Candidate/Active rolls: {wallet_candidate_rolls}/{wallet_active_rolls}",
                f"🥊 Missed blocks: {wallet_missed_blocks}", "",
                "🔎 Detailed info:", "",
                f"🧵 Thread: {wallet_thread}", "",
                *cycles_list, "",
                *credit_list,
            )
        await message.answer(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )

    await state.clear()
    return
