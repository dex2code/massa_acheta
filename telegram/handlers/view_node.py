from loguru import logger

from time import time as t_now
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.formatting import as_list, as_line, Code
from aiogram.enums import ParseMode

import app_globals
from telegram.keyboards.kb_nodes import kb_nodes
from tools import get_list_nodes, get_last_seen, get_short_address


class NodeViewer(StatesGroup):
    waiting_node_name = State()

router = Router()


@router.message(StateFilter(None), Command("view_node"))
@logger.catch
async def cmd_view_node(message: Message, state: FSMContext) -> None:
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
        "❓ Tap the node to view or /cancel to quit the scenario.",
    )
    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        reply_markup=kb_nodes(),
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    await state.set_state(NodeViewer.waiting_node_name)
    return




@router.message(NodeViewer.waiting_node_name, F.text.in_(get_list_nodes()))
@logger.catch
async def show_node(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    if message.chat.id != app_globals.bot.chat_id: return

    node_name = message.text

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


    current_time = t_now()

    if len(app_globals.app_results[node_name]['wallets']) == 0:
        wallets_attached = "⭕ No wallets attached"
    else:
        wallets_attached = f"👛 Wallets attached: {len(app_globals.app_results[node_name]['wallets'])}"

    last_seen = get_last_seen(
        last_time=app_globals.app_results[node_name]['last_update'],
        current_time=current_time
    )

    if app_globals.app_results[node_name]['last_status'] != True:
        node_status = f"☠️ Status: Offline (last seen: {last_seen})"

        t = as_list(
            as_line(app_globals.app_config['telegram']['service_nickname']),
            as_line(
                "🏠 Node: ",
                Code(node_name),
                end=""
            ),
            f"📍 {app_globals.app_results[node_name]['url']}",
            f"{wallets_attached}", "",
            f"{node_status}", "",
            as_line("💻 Result: ", Code(app_globals.app_results[node_name]['last_result'])),
            f"⏳ Service checks updates: every {app_globals.app_config['service']['main_loop_period_sec']} seconds"
        )
    else:
        node_status = f"🌿 Status: Online (last seen: {last_seen})"

        node_id = app_globals.app_results[node_name]['last_result'].get("node_id", "Not known")
        node_ip = app_globals.app_results[node_name]['last_result'].get("node_ip", "Not known")

        node_version = app_globals.app_results[node_name]['last_result'].get("version", "Not known")
        if node_version != app_globals.current_massa_release:
            node_version += f" ❗ Update to {app_globals.current_massa_release}"

        current_cycle = app_globals.app_results[node_name]['last_result'].get("current_cycle", "Not known")
        chain_id = app_globals.app_results[node_name]['last_result'].get("chain_id", "Not known")

        if "network_stats" not in app_globals.app_results[node_name]['last_result']:
            in_connection_count = 0
            out_connection_count = 0
            known_peer_count = 0
            banned_peer_count = 0
        else:
            in_connection_count = app_globals.app_results[node_name]['last_result']['network_stats'].get("in_connection_count", 0)
            out_connection_count = app_globals.app_results[node_name]['last_result']['network_stats'].get("out_connection_count", 0)
            known_peer_count = app_globals.app_results[node_name]['last_result']['network_stats'].get("known_peer_count", 0)
            banned_peer_count = app_globals.app_results[node_name]['last_result']['network_stats'].get("banned_peer_count", 0)

        t = as_list(
            as_line(app_globals.app_config['telegram']['service_nickname']),
            as_line(
                "🏠 Node: ",
                Code(node_name),
                end=""
            ),
            f"📍 {app_globals.app_results[node_name]['url']}",
            f"{wallets_attached}", "",
            f"{node_status}", "",
            as_line(
                "🆔: ",
                Code(get_short_address(node_id))
            ),
            f"↕ Routable IP: {node_ip}", "",
            f"💾 Release: {node_version}", "",
            as_line(
                "🌀 Cycle: ",
                Code(current_cycle)
            ),
            f"↔ In/Out connections: {in_connection_count}/{out_connection_count}", "",
            f"🙋 Known/Banned peers: {known_peer_count}/{banned_peer_count}", "",
            as_line(
                "🔗 Chain ID: ",
                Code(chain_id)
            ),
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
