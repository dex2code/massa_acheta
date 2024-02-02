from loguru import logger

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.formatting import as_list, as_line, TextLink, Code
from aiogram.enums import ParseMode

import app_globals
from telegram.keyboards.kb_nodes import kb_nodes
from tools import get_short_address, save_app_results


class WalletAdder(StatesGroup):
    waiting_node_name = State()
    waiting_wallet_address = State()


router = Router()


@router.message(StateFilter(None), Command("add_wallet"))
@logger.catch
async def cmd_add_wallet(message: Message, state: FSMContext) -> None:
    logger.debug("->Enter Def")
    if message.chat.id != app_globals.bot.chat_id: return
    
    if len(app_globals.app_results) == 0:
        t = as_list(
                app_globals.app_config['telegram']['service_nickname'], "",
                "⭕ Node list is empty", "",
                "☝ Try /add_node to add a node or /help to learn bot commands"
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
            "❓ Tap the node to select or /cancel to quit the scenario:",
        )
    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        reply_markup=kb_nodes(),
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    await state.set_state(WalletAdder.waiting_node_name)
    return



@router.message(WalletAdder.waiting_node_name, F.text)
@logger.catch
async def input_wallet_to_add(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    if message.chat.id != app_globals.bot.chat_id: return

    node_name = message.text
    await state.set_data(data={"node_name": node_name})

    if node_name not in app_globals.app_results:
        t = as_list(
                as_line(app_globals.app_config['telegram']['service_nickname']),
                as_line(
                    "‼ Error: Unknown node ",
                    Code(node_name)
                ),
                "☝ Try /add_wallet to add another wallet or /help to learn bot commands"
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
            as_line(
                "❓ Please enter MASSA wallet address with leading ",
                Code("AU..."),
                " prefix or /cancel to quit the scenario:"
            )
        )
    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove(),
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    await state.set_state(WalletAdder.waiting_wallet_address)
    return



@router.message(WalletAdder.waiting_wallet_address, F.text.startswith("AU"))
@logger.catch
async def add_wallet(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    if message.chat.id != app_globals.bot.chat_id: return

    user_state = await state.get_data()
    node_name = user_state['node_name']
    wallet_address = message.text

    if wallet_address in app_globals.app_results[node_name]['wallets']:
        t = as_list(
                as_line(app_globals.app_config['telegram']['service_nickname']),
                as_line(
                    "‼ Error: Wallet ",
                    TextLink(
                        get_short_address(address=wallet_address),
                        url=f"{app_globals.app_config['service']['mainnet_explorer']}/address/{wallet_address}"
                    ),
                    f" already attached to node ",
                    Code(node_name)
                ),
                "☝ Try /add_wallet to add another wallet or /help to learn bot commands"
            )
        await message.answer(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )

        await state.clear()
        return

    try:
        async with app_globals.results_lock:
            app_globals.app_results[node_name]['wallets'][wallet_address] = {}
            app_globals.app_results[node_name]['wallets'][wallet_address]['final_balance'] = 0
            app_globals.app_results[node_name]['wallets'][wallet_address]['candidate_rolls'] = 0
            app_globals.app_results[node_name]['wallets'][wallet_address]['active_rolls'] = 0
            app_globals.app_results[node_name]['wallets'][wallet_address]['missed_blocks'] = 0
            app_globals.app_results[node_name]['wallets'][wallet_address]['last_status'] = "unknown"
            app_globals.app_results[node_name]['wallets'][wallet_address]['last_update'] = 0
            app_globals.app_results[node_name]['wallets'][wallet_address]['last_result'] = {"unknown": "Never updated before"}
            await save_app_results()

    except Exception as E:
        logger.error(f"Cannot add wallet '{wallet_address}' to node '{node_name}': ({str(E)})")
        t = as_list(
                as_line(app_globals.app_config['telegram']['service_nickname']),
                as_line(
                    "‼ Error: Could not add wallet ",
                    TextLink(
                        get_short_address(wallet_address),
                        url=f"{app_globals.app_config['service']['mainnet_explorer']}/address/{wallet_address}"
                    ),
                    " to node ",
                    Code(node_name)
                ),
                as_line(
                    "💻 Result: ",
                    Code(str(E))
                ),
                as_line(
                    "⚠ Try again later or watch logs to check the reason - ",
                    TextLink(
                        "More info here",
                        url="https://github.com/dex2code/massa_acheta/blob/main/README.md"
                    )
                )
            )

    else:
        logger.info(f"Successfully added wallet '{wallet_address}' to node '{node_name}'")
        t = as_list(
                as_line(app_globals.app_config['telegram']['service_nickname']),
                as_line(
                    "✅ Successfully added wallet: ",
                    TextLink(
                        get_short_address(wallet_address),
                        url=f"{app_globals.app_config['service']['mainnet_explorer']}/address/{wallet_address}"
                    )
                ),
                as_line(
                    "🏠 Node: ",
                    Code(node_name),
                    end=""
                ),
                f"📍 {app_globals.app_results[node_name]['url']}", "",
                "👁 You can check new settings using /view_config command", "",
                "☝ Please note that info for this wallet will be updated a bit later!"
            )


    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    await state.clear()
    return
