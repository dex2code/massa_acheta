from loguru import logger

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.formatting import as_list, as_line, TextLink, Code
from aiogram.enums import ParseMode

from app_config import app_config
import app_globals

from telegram.keyboards.kb_nodes import kb_nodes
from telegram.keyboards.kb_wallets import kb_wallets
from tools import get_short_address, save_app_results, check_privacy


class WalletRemover(StatesGroup):
    waiting_node_name = State()
    waiting_wallet_address = State()

router = Router()


@router.message(StateFilter(None), Command("delete_wallet"))
@logger.catch
async def cmd_delete_wallet(message: Message, state: FSMContext) -> None:
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
        "❓ Tap the node to select or /cancel to quit the scenario:",
    )
    try:
        await state.set_state(WalletRemover.waiting_node_name)
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



@router.message(WalletRemover.waiting_node_name, F.text)
@logger.catch
async def select_wallet_to_delete(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from '{message.from_user.id}'@'{message.chat.id}'")
    if not await check_privacy(message=message): return

    node_name = message.text
    if node_name not in app_globals.app_results:
        t = as_list(
            f"‼ Error: Unknown node \"{node_name}\"", "",
            "👉 Try /delete_wallet to delete another wallet or /help to learn bot commands"
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
            f"⭕ No wallets attached to node \"{node_name}\"", "",
            "👉 Try /add_wallet to add a wallet or /help to learn bot commands"
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
        await state.set_state(WalletRemover.waiting_wallet_address)
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



@router.message(WalletRemover.waiting_wallet_address, F.text.startswith("AU"))
@logger.catch
async def delete_wallet(message: Message, state: FSMContext) -> None:
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
                f" is not attached to node {node_name}"
            ),
            "👉 Try /delete_wallet to delete another wallet or /help to learn bot commands"
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

    try:
        async with app_globals.results_lock:
            app_globals.app_results[node_name]['wallets'].pop(wallet_address, None)
            save_app_results()

    except BaseException as E:
        logger.error(f"Cannot remove wallet '{wallet_address}' from node '{node_name}': ({str(E)})")

        t = as_list(
            as_line(
                "‼ Error: Could not delete wallet ",
                TextLink(
                    await get_short_address(wallet_address),
                    url=f"{app_config['service']['mainnet_explorer_url']}/address/{wallet_address}"
                ),
                " from node ",
                Code(await get_short_address(node_name)),
            ),
            as_line(
                "💻 Result: ",
                Code(str(E))
            ),
            as_line(
                "⚠ Try again later or watch logs to check the reason - ",
                TextLink(
                    "More info here",
                    url="https://github.com/dex2code/massa_acheta/"
                )
            )
        )

    else:
        logger.info(f"Successfully removed wallet '{wallet_address}' from node '{node_name}'")

        t = as_list(
            as_line(
                "👌 Successfully removed wallet ",
                TextLink(
                    await get_short_address(wallet_address),
                    url=f"{app_config['service']['mainnet_explorer_url']}/address/{wallet_address}"
                ),
                " from node ",
                Code(await get_short_address(node_name)),
            ),
            "👉 You can check new settings using /view_config command"
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
