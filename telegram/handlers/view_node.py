from loguru import logger

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.formatting import as_list, as_line, Code
from aiogram.enums import ParseMode

from app_config import app_config
import app_globals

from telegram.keyboards.kb_nodes import kb_nodes
from tools import get_last_seen, get_short_address, check_privacy


class NodeViewer(StatesGroup):
    waiting_node_name = State()

router = Router()


@router.message(StateFilter(None), Command("view_node"))
@logger.catch
async def cmd_view_node(message: Message, state: FSMContext) -> None:
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
        "👉 Tap the node to view or /cancel to quit the scenario",
    )
    try:
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            reply_markup=kb_nodes(),
            request_timeout=app_config['telegram']['sending_timeout_sec']
        )
        await state.set_state(NodeViewer.waiting_node_name)
    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")
        await state.clear()

    return



@router.message(NodeViewer.waiting_node_name, F.text)
@logger.catch
async def show_node(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from '{message.from_user.id}'@'{message.chat.id}'")
    if not await check_privacy(message=message): return

    node_name = message.text

    if node_name not in app_globals.app_results:
        t = as_list(
            f"‼ Error: Unknown node \"{node_name}\"", "",
            "👉 Try /view_node to view another node or /help to learn how to add a node to bot"
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
        wallets_attached = "⭕ No wallets attached"
    else:
        wallets_attached = f"👛 Wallets attached: {len(app_globals.app_results[node_name]['wallets'])}"

    last_seen = await get_last_seen(
        last_time=app_globals.app_results[node_name]['last_update']
    )

    if app_globals.app_results[node_name]['last_status'] != True:
        node_status = f"☠️ Status: Offline (last seen: {last_seen})"

        t = as_list(
            f"🏠 Node: \"{node_name}\"",
            f"📍 {app_globals.app_results[node_name]['url']}",
            f"{wallets_attached}", "",
            f"{node_status}", "",
            as_line(
                "💻 Result: ",
                Code(app_globals.app_results[node_name]['last_result'])
            ),
            f"☝ Service checks updates: every {app_config['service']['main_loop_period_min']} minutes"
        )
    else:
        node_status = f"🌿 Status: Online (last seen: {last_seen})"

        node_id = app_globals.app_results[node_name]['last_result'].get("node_id", "Not known")
        node_ip = app_globals.app_results[node_name]['last_result'].get("node_ip", "Not known")

        node_version = app_globals.app_results[node_name]['last_result'].get("version", "Not known")
        if node_version != app_globals.massa_network['values']['latest_release']:
            node_update_needed = f"❗ Update to \"{app_globals.massa_network['values']['latest_release']}\""
        else:
            node_update_needed = "(latest)"

        current_cycle = app_globals.app_results[node_name]['last_cycle']
        chain_id = app_globals.app_results[node_name]['last_chain_id']

        in_connection_count = app_globals.app_results[node_name]['last_result']['network_stats'].get("in_connection_count", 0)
        out_connection_count = app_globals.app_results[node_name]['last_result']['network_stats'].get("out_connection_count", 0)
        known_peer_count = app_globals.app_results[node_name]['last_result']['network_stats'].get("known_peer_count", 0)
        banned_peer_count = app_globals.app_results[node_name]['last_result']['network_stats'].get("banned_peer_count", 0)

        t = as_list(
            f"🏠 Node: \"{node_name}\"",
            f"📍 {app_globals.app_results[node_name]['url']}",
            f"{wallets_attached}", "",
            f"{node_status}", "",
            f"🆔: {await get_short_address(node_id)}", "",
            f"🎯 Routable IP: {node_ip}", "",
            f"💾 Release: \"{node_version}\" {node_update_needed}", "",
            f"🌀 Cycle: {current_cycle}", "",
            f"↔ In / Out connections: {in_connection_count} / {out_connection_count}", "",
            f"🙋 Known / Banned peers: {known_peer_count} / {banned_peer_count}", "",
            f"🔗 Chain ID: {chain_id}", "",
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
