from loguru import logger

from time import time as t_now
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.formatting import as_list, as_line, Code, Pre
from aiogram.enums import ParseMode

from app_globals import app_config, app_results, bot
from telegram.keyboards.kb_nodes import kb_nodes
from tools import get_list_nodes, get_last_seen


class NodeViewer(StatesGroup):
    waiting_node_name = State()

router = Router()


@router.message(StateFilter(None), Command("view_node"))
@logger.catch
async def cmd_view_node(message: Message, state: FSMContext):
    logger.debug("->Enter Def")
    if message.chat.id != bot.chat_id: return
    
    if len(app_results) == 0:
        t = as_list(
            app_config['telegram']['service_nickname'], "",
            "⭕ Node list is empty.", "",
            "❓ Try /help to learn how to add a node to bot."
        )
        await message.answer(text=t.as_html())
        await state.clear()
        return


    t = as_list(
        as_line(app_config['telegram']['service_nickname']),
        "❓ Tap the node to view info or /cancel to quit the scenario.",
    )
    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        reply_markup=kb_nodes(),
        request_timeout=app_config['telegram']['sending_timeout_sec']
    )

    await state.set_state(NodeViewer.waiting_node_name)




@router.message(NodeViewer.waiting_node_name, F.text.in_(get_list_nodes()))
@logger.catch
async def show_node(message: Message, state: FSMContext):
    logger.debug("-> Enter Def")
    if message.chat.id != bot.chat_id: return

    node_name = message.text

    if node_name not in app_results:
        t = as_list(
            as_line(app_config['telegram']['service_nickname']),
            "‼ Error. Unknown node.", "",
            "❓ Try /help to learn how to add a node to bot."
        )
        await message.answer(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_config['telegram']['sending_timeout_sec']
        )

        return


    current_time = t_now()

    if len(app_results[node_name]['wallets']) == 0:
        wallets_attached = "⭕ No wallets attached"
    else:
        wallets_attached = f"👛 Wallets attached: {len(app_results[node_name]['wallets'])}"

    if app_results[node_name]['last_status'] == True:
        node_status = "🌿 Online"
    else:
        node_status = "☠️ Offline"

    last_seen = get_last_seen(
        last_time=app_results[node_name]['last_update'],
        current_time=current_time
    )

    node_id = app_results[node_name]['last_result'].get("node_id", "Not known")
    node_ip = app_results[node_name]['last_result'].get("node_ip", "Not known")
    node_version = app_results[node_name]['last_result'].get("version", "Not known")
    current_cycle = app_results[node_name]['last_result'].get("current_cycle", "Not known")
    chain_id = app_results[node_name]['last_result'].get("chain_id", "Not known")

    if "network_stats" not in app_results[node_name]['last_result']:
        in_connection_count = 0
        out_connection_count = 0
        known_peer_count = 0
        banned_peer_count = 0
    else:
        in_connection_count = app_results[node_name]['last_result']['network_stats'].get("in_connection_count", 0)
        out_connection_count = app_results[node_name]['last_result']['network_stats'].get("out_connection_count", 0)
        known_peer_count = app_results[node_name]['last_result']['network_stats'].get("known_peer_count", 0)
        banned_peer_count = app_results[node_name]['last_result']['network_stats'].get("banned_peer_count", 0)

    t = as_list(
        as_line(app_config['telegram']['service_nickname']),
        as_line("🏠 Node: ", Code(node_name), end=""),
        f"📍 {app_results[node_name]['url']}",
        f"{wallets_attached}", "",
        f"{node_status} (last seen: {last_seen})", "",
        f"Node 🆔:", Pre(node_id), "",
        f"↔ Routable IP: {node_ip}", "",
        f"💾 Release: {node_version}", "",
        f"🌀 Cycle: {current_cycle}", "",
        f"↔ In/Out connections: {in_connection_count}/{out_connection_count}", "",
        f"🙋 Known/Banned peers: {known_peer_count}/{banned_peer_count}", "",
        f"🔗 Chain ID: {chain_id}"
    )
    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove(),
        request_timeout=app_config['telegram']['sending_timeout_sec']
    )

    await state.clear()



