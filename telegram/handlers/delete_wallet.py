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
from telegram.keyboards.kb_wallets import kb_wallets
from tools import get_list_nodes, get_all_wallets, get_short_address, save_app_results


class WalletRemover(StatesGroup):
    waiting_node_name = State()
    waiting_wallet_address = State()


router = Router()


@router.message(StateFilter(None), Command("delete_wallet"))
@logger.catch
async def cmd_delete_wallet(message: Message, state: FSMContext) -> None:
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

    await state.set_state(WalletRemover.waiting_node_name)
    return



@router.message(WalletRemover.waiting_node_name, F.text.in_(get_list_nodes()))
@logger.catch
async def select_wallet_to_delete(message: Message, state: FSMContext) -> None:
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

    await state.set_state(WalletRemover.waiting_wallet_address)
    return



@router.message(WalletRemover.waiting_wallet_address, F.text.in_(get_all_wallets()))
@logger.catch
async def delete_wallet(message: Message, state: FSMContext) -> None:
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
            reply_markup=ReplyKeyboardRemove(),
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )
        await state.clear()
        return

    try:
        async with app_globals.results_lock:
            del app_globals.app_results[node_name]['wallets'][wallet_address]
            await save_app_results()

    except Exception as E:
        logger.error(f"Cannot remove wallet '{wallet_address}' from node '{node_name}': ({str(E)})")

        t = as_list(
                as_line(app_globals.app_config['telegram']['service_nickname']),
                as_line(
                    "‼ Error removing wallet ",
                    TextLink(
                        get_short_address(wallet_address),
                        url=f"{app_globals.app_config['service']['mainnet_explorer']}/address/{wallet_address}"
                    ),
                    " from node ",
                    Code(get_short_address(node_name)),
                ),
                as_line(
                    "⚠ Try again later or watch logs to check the reason. ",
                    TextLink(
                        "More info here",
                        url="https://github.com/dex2code/massa_acheta/blob/main/README.md"
                    )
                )
            )

    else:
        logger.info(f"Successfully removed wallet '{wallet_address}' from node '{node_name}'")

        t = as_list(
                as_line(app_globals.app_config['telegram']['service_nickname']),
                as_line(
                    "✅ Successfully removed wallet ",
                    TextLink(
                        get_short_address(wallet_address),
                        url=f"{app_globals.app_config['service']['mainnet_explorer']}/address/{wallet_address}"
                    ),
                    " from node ",
                    Code(get_short_address(node_name)),
                ),
                "👁 You can check new settings using /view_config command"
            )


    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove(),
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    await state.clear()
    return
