from loguru import logger

from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.formatting import as_list, as_line, TextLink
from aiogram.enums import ParseMode
from quickchart import QuickChart

import app_globals
from telegram.keyboards.kb_nodes import kb_nodes
from telegram.keyboards.kb_wallets import kb_wallets
from tools import get_short_address, get_last_seen, check_privacy, get_rewards


class ChartWalletViewer(StatesGroup):
    waiting_node_name = State()
    waiting_wallet_address = State()

router = Router()


@router.message(StateFilter(None), Command("chart_wallet"))
@logger.catch
async def cmd_chart_wallet(message: Message, state: FSMContext) -> None:
    logger.debug("->Enter Def")
    logger.info(f"-> Got '{message.text}' command from user '{message.from_user.id}' in chat '{message.chat.id}'")
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
                request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
            )
        except BaseException as E:
            logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

        await state.clear()
        return


    t = as_list(
        "❓ Tap the node to select or /cancel to quit the scenario",
    )
    try:
        await state.set_state(ChartWalletViewer.waiting_node_name)
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            reply_markup=kb_nodes(),
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )
    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")
        await state.clear()

    return



@router.message(ChartWalletViewer.waiting_node_name, F.text)
@logger.catch
async def select_wallet_to_show(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from user '{message.from_user.id}' in chat '{message.chat.id}'")
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
                request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
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
                request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
            )
        except BaseException as E:
            logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

        await state.clear()
        return

    t = as_list(
        "❓ Tap the wallet to select or /cancel to quit the scenario:",
    )
    try:
        await state.set_state(ChartWalletViewer.waiting_wallet_address)
        await state.set_data(data={"node_name": node_name})
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            reply_markup=kb_wallets(node_name=node_name),
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )
    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")
        await state.clear()

    return



@router.message(ChartWalletViewer.waiting_wallet_address, F.text.startswith("AU"))
@logger.catch
async def show_wallet(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from user '{message.from_user.id}' in chat '{message.chat.id}'")
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
                    get_short_address(address=wallet_address),
                    url=f"{app_globals.app_config['service']['mainnet_explorer_url']}/address/{wallet_address}"
                ),
                f" is not attached to node \"{node_name}\""
            ),
            "👉 Try /view_wallet to view another wallet or /help to learn bot commands"
        )
        try:
            await message.reply(
                text=t.as_html(),
                parse_mode=ParseMode.HTML,
                request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
            )
        except BaseException as E:
            logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

        await state.clear()
        return

    chart_config = {
        "type": "line",

        "options": {

            "title": {
                "display": True,
                "text": f"Wallet {get_short_address(address=wallet_address)} chart"
            },

            "scales": {
                "yAxes": [
                    {
                        "id": "balance",
                        "display": True,
                        "position": "left",
                        "ticks": { "fontColor": "blue" },
                        "gridLines": { "drawOnChartArea": False }
                    },
                    {
                        "id": "rolls",
                        "display": True,
                        "position": "right",
                        "ticks": { "fontColor": "red" },
                        "gridLines": { "drawOnChartArea": False }
                    }
                ]
            }
        },

        "data": {
            "labels": [],

            "datasets": [
                {
                    "label": "Final balance",
                    "yAxisID": "balance",
                    "lineTension": 0.4,
                    "fill": False,
                    "borderColor": "blue",
                    "borderWidth": 1,
                    "pointRadius": 0,
                    "data": []
                },
                {
                    "label": "Rolls staked",
                    "yAxisID": "rolls",
                    "lineTension": 0.4,
                    "fill": False,
                    "borderColor": "red",
                    "borderWidth": 1,
                    "pointRadius": 0,
                    "data": []
                }
            ]
        }
    }

    try:
        for measure in app_globals.app_results[node_name]['wallets'][wallet_address]['stat']:

            label = measure['time']
            label = datetime.utcfromtimestamp(label).strftime("%b, %-d")

            rolls = measure['rolls']
            balance = measure['balance']

            chart_config['data']['labels'].append(label)
            chart_config['data']['datasets'][0]['data'].append(balance)
            chart_config['data']['datasets'][1]['data'].append(rolls)

        chart = QuickChart()
        chart.device_pixel_ratio = 2.0
        chart.width = 600
        chart.height = 300
        chart.config = chart_config
        chart_url = chart.get_url()

    except BaseException as E:
        logger.error(f"Cannot prepare wallet chart ({str(E)})")
        t = as_list(
            as_line("🤷 Charts are temporary unavailable. Try later."),
            as_line("☝ Use /help to learn bot commands")
        )
        try:
            await message.reply(
                text=t.as_html(),
                parse_mode=ParseMode.HTML,
                reply_markup=ReplyKeyboardRemove(),
                request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
            )
        except BaseException as E:
            logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    else:
        try:
            await message.reply_photo(
                photo=chart_url,
                parse_mode=ParseMode.HTML,
                reply_markup=ReplyKeyboardRemove(),
                request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
            )
        except BaseException as E:
            logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    await state.clear()
    return
