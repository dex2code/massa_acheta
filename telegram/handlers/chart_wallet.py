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

from app_config import app_config
import app_globals

from telegram.keyboards.kb_nodes import kb_nodes
from telegram.keyboards.kb_wallets import kb_wallets
from tools import get_short_address, check_privacy, get_rewards


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
        await state.set_state(ChartWalletViewer.waiting_node_name)
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
        await state.set_state(ChartWalletViewer.waiting_wallet_address)
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

    staking_chart_config = {
        "type": "line",

        "options": {

            "title": {
                "display": True,
                "text": f"Wallet: {get_short_address(address=wallet_address)}"
            },

            "scales": {
                "yAxes": [
                    {
                        "id": "rolls",
                        "display": True,
                        "position": "left",
                        "ticks": { "fontColor": "green" },
                        "gridLines": { "drawOnChartArea": False }
                    },
                    {
                        "id": "balance",
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
                    "label": "Rolls staked",
                    "yAxisID": "rolls",
                    "lineTension": 0.4,
                    "fill": False,
                    "borderColor": "green",
                    "borderWidth": 1,
                    "pointRadius": 0,
                    "data": []
                },
                {
                    "label": "Final balance",
                    "yAxisID": "balance",
                    "lineTension": 0.4,
                    "fill": False,
                    "borderColor": "red",
                    "borderWidth": 2,
                    "pointRadius": 0,
                    "data": []
                }
            ]
        }
    }

    blocks_chart_config = {
        "type": "bar",

        "options": {

            "title": {
                "display": True,
                "text": f"Wallet: {get_short_address(address=wallet_address)}"
            },

            "scales": {

                "yAxes": [
                    {
                        "id": "blocks",
                        "display": True,
                        "position": "left",
                        "stacked": True,
                        "ticks": { "min": 0, "fontColor": "black" },
                        "gridLines": { "drawOnChartArea": False }
                    },
                    {
                        "id": "earnings",
                        "display": True,
                        "position": "right",
                        "stacked": False,
                        "ticks": { "fontColor": "blue" },
                        "gridLines": { "drawOnChartArea": False }
                    }
                ],
                "xAxes": [ { "stacked": True } ]
            }
        },

        "data": {

            "labels": [],

            "datasets": [
                {
                    "type": "line",
                    "label": "Estimated earnings (MAS)",
                    "yAxisID": "earnings",
                    "lineTension": 0.4,
                    "fill": False,
                    "borderColor": "blue",
                    "borderWidth": 2,
                    "pointRadius": 0,
                    "data": []
                },
                {
                    "type": "bar",
                    "label": "Operated blocks",
                    "yAxisID": "blocks",
                    "backgroundColor": "green",
                    "data": []
                },
                {
                    "type": "bar",
                    "label": "Missed blocks",
                    "yAxisID": "blocks",
                    "backgroundColor": "red",
                    "data": []
                },
            ]
        }
    }

    try:
        wallet_stat_keytime_unsorted = {}
        for measure in app_globals.app_results[node_name]['wallets'][wallet_address]['stat']:
            measure_time = measure['time']
            measure_cycle = measure['cycle']
            measure_balance = measure['balance']
            measure_rolls = measure['rolls']
            measure_ok_blocks = measure['ok_blocks']
            measure_nok_blocks = measure['nok_blocks']

            wallet_stat_keytime_unsorted[measure_time] = {
                "cycle": measure_cycle,
                "balance": measure_balance,
                "rolls": measure_rolls,
                "ok_blocks": measure_ok_blocks,
                "nok_blocks": measure_nok_blocks
            }

        wallet_stat_keytime_sorted = dict(
            sorted(
                wallet_stat_keytime_unsorted.items()
            )
        )

        wallet_stat_keycycle_unsorted = {}
        for measure in wallet_stat_keytime_sorted:
            measure_cycle = wallet_stat_keytime_sorted[measure]['cycle']
            measure_balance = wallet_stat_keytime_sorted[measure]['balance']
            measure_rolls = wallet_stat_keytime_sorted[measure]['rolls']
            measure_ok_blocks = wallet_stat_keytime_sorted[measure]['ok_blocks']
            measure_nok_blocks = wallet_stat_keytime_sorted[measure]['nok_blocks']

            wallet_stat_keycycle_unsorted[measure_cycle] = {
                "balance": measure_balance,
                "rolls": measure_rolls,
                "ok_blocks": measure_ok_blocks,
                "nok_blocks": measure_nok_blocks
            }

        wallet_stat_keycycle_sorted = dict(
            sorted(
                wallet_stat_keycycle_unsorted.items()
            )
        )

        for cycle in wallet_stat_keycycle_sorted:
            balance = wallet_stat_keycycle_sorted[cycle]['balance']
            rolls = wallet_stat_keycycle_sorted[cycle]['rolls']
            ok_blocks = wallet_stat_keycycle_sorted[cycle]['ok_blocks']
            nok_blocks = wallet_stat_keycycle_sorted[cycle]['nok_blocks']

            staking_chart_config['data']['labels'].append(cycle)
            staking_chart_config['data']['datasets'][0]['data'].append(rolls)
            staking_chart_config['data']['datasets'][1]['data'].append(balance)

            blocks_chart_config['data']['labels'].append(cycle)
            blocks_chart_config['data']['datasets'][0]['data'].append(get_rewards(rolls_number=rolls))
            blocks_chart_config['data']['datasets'][1]['data'].append(ok_blocks)
            blocks_chart_config['data']['datasets'][2]['data'].append(nok_blocks)

        staking_chart = QuickChart()
        staking_chart.device_pixel_ratio = 2.0
        staking_chart.width = 600
        staking_chart.height = 300
        staking_chart.config = staking_chart_config
        staking_chart_url = staking_chart.get_url()

        blocks_chart = QuickChart()
        blocks_chart.device_pixel_ratio = 2.0
        blocks_chart.width = 600
        blocks_chart.height = 300
        blocks_chart.config = blocks_chart_config
        blocks_chart_url = blocks_chart.get_url()

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
                request_timeout=app_config['telegram']['sending_timeout_sec']
            )
        except BaseException as E:
            logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    else:
        try:
            await message.answer_photo(
                photo=staking_chart_url,
                caption="Staking chart",
                parse_mode=ParseMode.HTML,
                reply_markup=ReplyKeyboardRemove(),
                request_timeout=app_config['telegram']['sending_timeout_sec']
            )
            await message.answer_photo(
                photo=blocks_chart_url,
                caption="Blocks chart",
                parse_mode=ParseMode.HTML,
                reply_markup=ReplyKeyboardRemove(),
                request_timeout=app_config['telegram']['sending_timeout_sec']
            )
        except BaseException as E:
            logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    await state.clear()
    return
