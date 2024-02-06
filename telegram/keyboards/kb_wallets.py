from loguru import logger

from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import app_globals


def kb_wallets(node_name: str="") -> ReplyKeyboardMarkup:
    logger.debug("-> Enter Def")

    if node_name not in app_globals.app_results:
        return ReplyKeyboardBuilder().as_markup()

    try:
        wallet_keyboard = ReplyKeyboardBuilder()

        for wallet_address in app_globals.app_results[node_name]['wallets']:
            wallet_keyboard.button(text=wallet_address)

        wallet_keyboard.adjust(1)
    
    except BaseException as E:
        logger.error(f"Cannot build node_keyboard: ({str(E)})")
        return ReplyKeyboardBuilder().as_markup()

    return wallet_keyboard.as_markup(resize_keyboard=True)
