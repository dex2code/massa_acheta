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
from tools import get_short_address, check_privacy, get_rewards_mas_day, get_rewards_blocks_cycle


class ChartWalletViewer(StatesGroup):
    waiting_node_name = State()
    waiting_wallet_address = State()

router = Router()


@router.message(StateFilter(None), Command("chart_wallet"))
@logger.catch
async def cmd_chart_wallet(message: Message, state: FSMContext) -> None:
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

    staking_chart_config = {
        "type": "line",

        "options": {

            "title": {
                "display": True,
                "text": f"Wallet: {await get_short_address(address=wallet_address)}"
            },

            "scales": {
                "yAxes": [
                    {
                        "id": "rolls",
                        "display": True,
                        "position": "left",
                        "ticks": { "fontColor": "Teal" },
                        "gridLines": { "drawOnChartArea": False }
                    },
                    {
                        "id": "balance",
                        "display": True,
                        "position": "right",
                        "ticks": { "fontColor": "FireBrick" },
                        "gridLines": { "drawOnChartArea": True }
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
                    "borderColor": "Teal",
                    "borderWidth": 2,
                    "pointRadius": 2,
                    "data": []
                },
                {
                    "label": "Final balance",
                    "yAxisID": "balance",
                    "lineTension": 0.4,
                    "fill": False,
                    "borderColor": "FireBrick",
                    "borderWidth": 2,
                    "pointRadius": 2,
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
                "text": f"Wallet: {await get_short_address(address=wallet_address)}"
            },

            "scales": {

                "yAxes": [
                    {
                        "id": "blocks",
                        "display": True,
                        "position": "left",
                        "stacked": True,
                        "ticks": { "min": 0, "fontColor": "LightSeaGreen" },
                        "gridLines": { "drawOnChartArea": False }
                    },
                    {
                        "id": "earnings",
                        "display": True,
                        "position": "right",
                        "stacked": False,
                        "ticks": { "fontColor": "DarkViolet" },
                        "gridLines": { "drawOnChartArea": True }
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
                    "label": "Est. MAS / Day",
                    "yAxisID": "earnings",
                    "lineTension": 0.4,
                    "fill": False,
                    "borderColor": "DarkViolet",
                    "borderWidth": 2,
                    "pointRadius": 2,
                    "data": []
                },
                {
                    "type": "bar",
                    "label": "OK blocks",
                    "yAxisID": "blocks",
                    "backgroundColor": "LightSeaGreen",
                    "data": []
                },
                {
                    "type": "bar",
                    "label": "nOK blocks",
                    "yAxisID": "blocks",
                    "backgroundColor": "LightSalmon",
                    "data": []
                },
                {
                    "type": "line",
                    "label": "Est. Blocks / Cycle",
                    "yAxisID": "blocks",
                    "lineTension": 0.4,
                    "fill": True,
                    "borderColor": "lightgray",
                    "backgroundColor": "rgba(220, 220, 220, 0.4)",
                    "borderWidth": 0,
                    "pointRadius": 0,
                    "data": []
                }
            ]
        }
    }

    try:
        wallet_stat_keytime_unsorted = {}
        for measure in app_globals.app_results[node_name]['wallets'][wallet_address].get("stat", {}):
            measure_time = measure.get("time", 0)
            measure_cycle = measure.get("cycle", 0)
            measure_balance = measure.get("balance", 0)
            measure_rolls = measure.get("rolls", 0)
            measure_total_rolls = measure.get("total_rolls", 0)
            measure_ok_blocks = measure.get("ok_blocks", 0)
            measure_nok_blocks = measure.get("nok_blocks", 0)

            wallet_stat_keytime_unsorted[measure_time] = {
                "cycle": measure_cycle,
                "balance": measure_balance,
                "rolls": measure_rolls,
                "total_rolls": measure_total_rolls,
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
            measure_cycle = wallet_stat_keytime_sorted[measure].get("cycle", 0)
            measure_balance = wallet_stat_keytime_sorted[measure].get("balance", 0)
            measure_rolls = wallet_stat_keytime_sorted[measure].get("rolls", 0)
            measure_total_rolls = wallet_stat_keytime_sorted[measure].get("total_rolls", 0)
            measure_ok_blocks = wallet_stat_keytime_sorted[measure].get("ok_blocks", 0)
            measure_nok_blocks = wallet_stat_keytime_sorted[measure].get("nok_blocks", 0)

            wallet_stat_keycycle_unsorted[measure_cycle] = {
                "balance": measure_balance,
                "rolls": measure_rolls,
                "total_rolls": measure_total_rolls,
                "ok_blocks": measure_ok_blocks,
                "nok_blocks": measure_nok_blocks
            }

        wallet_stat_keycycle_sorted = dict(
            sorted(
                wallet_stat_keycycle_unsorted.items()
            )
        )

        total_cycles = len(wallet_stat_keycycle_sorted)
        total_blocks = 0
        total_rewards_block_cycle = 0
        delta_balance, delta_rolls = 0, 0
        last_balance, last_rolls = 0, 0

        for cycle in wallet_stat_keycycle_sorted:
            balance = wallet_stat_keycycle_sorted[cycle].get("balance", 0)
            if last_balance == 0:
                last_balance = balance
            delta_balance += balance - last_balance
            last_balance = balance

            rolls = wallet_stat_keycycle_sorted[cycle].get("rolls", 0)
            if last_rolls == 0:
                last_rolls = rolls
            delta_rolls += rolls - last_rolls
            last_rolls = rolls

            total_rolls = wallet_stat_keycycle_sorted[cycle].get("total_rolls", 0)
            ok_blocks = wallet_stat_keycycle_sorted[cycle].get("ok_blocks", 0)
            nok_blocks = wallet_stat_keycycle_sorted[cycle].get("nok_blocks", 0)
            total_blocks += (ok_blocks + nok_blocks)

            staking_chart_config['data']['labels'].append(cycle)
            staking_chart_config['data']['datasets'][0]['data'].append(rolls)
            staking_chart_config['data']['datasets'][1]['data'].append(balance)

            blocks_chart_config['data']['labels'].append(cycle)
            rewards_mas_day = await get_rewards_mas_day(rolls_number=rolls, total_rolls=total_rolls)
            blocks_chart_config['data']['datasets'][0]['data'].append(rewards_mas_day)

            blocks_chart_config['data']['datasets'][1]['data'].append(ok_blocks)
            blocks_chart_config['data']['datasets'][2]['data'].append(nok_blocks)

            rewards_blocks_cycle = await get_rewards_blocks_cycle(rolls_number=rolls, total_rolls=total_rolls)
            blocks_chart_config['data']['datasets'][3]['data'].append(rewards_blocks_cycle)
            total_rewards_block_cycle += rewards_blocks_cycle
        
        fact_blocks_per_cycle = round(
            (total_blocks) / total_cycles,
            4
        )

        est_blocks_per_cycle = round(
            total_rewards_block_cycle / total_cycles,
            4
        )

        delta_balance = delta_rolls * app_globals.massa_network['values']['roll_price'] + delta_balance
        delta_balance = round(delta_balance, 4)
        if delta_balance > 0: delta_balance = f"+{delta_balance:,}"
        else: delta_balance = f"{delta_balance:,}"

        if delta_rolls > 0: delta_rolls = f"+{delta_rolls:,}"
        else: delta_rolls = f"{delta_rolls:,}"
        
        caption_staking = as_list(
            f"Cycles collected: {total_cycles:,}",
            f"Current balance: {balance:,} MAS (d: {delta_balance})",
            f"Number of rolls: {rolls:,} (d: {delta_rolls})",
        )

        caption_blocks = as_list(
            f"Cycles collected: {total_cycles:,}",
            f"Operated blocks: {total_blocks:,}",
            f"Estimated Blocks / Cycle: {est_blocks_per_cycle:,}",
            f"Fact Blocks / Cycle: {fact_blocks_per_cycle:,}"
        )

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
                caption=caption_staking.as_html(),
                parse_mode=ParseMode.HTML,
                reply_markup=ReplyKeyboardRemove(),
                request_timeout=app_config['telegram']['sending_timeout_sec']
            )

            await message.answer_photo(
                photo=blocks_chart_url,
                caption=caption_blocks.as_html(),
                parse_mode=ParseMode.HTML,
                reply_markup=ReplyKeyboardRemove(),
                request_timeout=app_config['telegram']['sending_timeout_sec']
            )
        except BaseException as E:
            logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    await state.clear()
    return
