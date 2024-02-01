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
from tools import get_list_nodes, get_short_address, save_app_results


class NodeAdder(StatesGroup):
    waiting_node_name = State()
    waiting_node_url = State()


router = Router()


@router.message(StateFilter(None), Command("add_node"))
@logger.catch
async def cmd_add_node(message: Message, state: FSMContext) -> None:
    logger.debug("->Enter Def")
    if message.chat.id != app_globals.bot.chat_id: return
    
    t = as_list(
            as_line(app_globals.app_config['telegram']['service_nickname']),
            "❓ Please enter a short name for the new node (nickname):",
        )
    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    await state.set_state(NodeAdder.waiting_node_name)
    return



@router.message(NodeAdder.waiting_node_name, F.text)
@logger.catch
async def input_nodename_to_add(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    if message.chat.id != app_globals.bot.chat_id: return

    node_name = message.text
    await state.set_data(data={"node_name": node_name})

    if node_name in app_globals.app_results:
        t = as_list(
                as_line(app_globals.app_config['telegram']['service_nickname']),
                as_line("‼ Error. Node nickname ",
                        Code(node_name),
                        " already exists!"
                ),
                as_line("❓ Try /help to learn how to add a node to bot")
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
            as_line(
                "❓ Please enter URL API for the new node ",
                Code(node_name),
                ":"
            ),
            "💭 Typically URL API looks like 'http://ip.ad.dre.ss:33035/api/v2'",
            "⚠ Please also check if you opened a firewall on the remote host!"
        )
    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    await state.set_state(NodeAdder.waiting_node_url)
    return



@router.message(NodeAdder.waiting_node_url, F.text)
@logger.catch
async def input_nodeurl_to_add(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    if message.chat.id != app_globals.bot.chat_id: return

    user_state = await state.get_data()
    node_name = user_state['node_name']
    node_url = message.text
    await state.set_data(data={"node_url": node_url})

    try:
        async with app_globals.results_lock:
            app_globals.app_results[node_name] = {}
            app_globals.app_results[node_name]['url'] = node_url
            app_globals.app_results[node_name]['last_status'] = "unknown"
            app_globals.app_results[node_name]['last_update'] = 0
            app_globals.app_results[node_name]['last_result'] = {"unknown": "Never updated before"}
            app_globals.app_results[node_name]['wallets'] = {}
            await save_app_results()

    except Exception as E:
        logger.error(f"Cannot add node '{node_name}' with URL '{node_url}': ({str(E)})")
        t = as_list(
                as_line(app_globals.app_config['telegram']['service_nickname']),
                as_line(
                    "‼ Error adding node ",
                    Code(get_short_address(node_name)),
                    f" with API URL {node_url}"
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
        logger.info(f"Successfully added node '{node_name}' with URL '{node_url}'")
        t = as_list(
                as_line(app_globals.app_config['telegram']['service_nickname']),
                as_line(
                    "✅ Successfully added node ",
                    Code(get_short_address(node_name)),
                    f" with API URL {node_url}"
                ),
                "👁 You can check new settings using /view_config command", "",
                "⚠ Please note that info for this node will be updated a bit later!"
            )


    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    await state.clear()
    return


