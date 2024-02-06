from loguru import logger

from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import app_globals


def kb_nodes() -> ReplyKeyboardMarkup:
    logger.debug("-> Enter Def")

    try:
        node_keyboard = ReplyKeyboardBuilder()

        for node_name in app_globals.app_results:
            node_keyboard.button(text=node_name)

        node_keyboard.adjust(2)

    except BaseException as E:
        logger.error(f"Cannot build node_keyboard: ({str(E)})")
        return ReplyKeyboardBuilder().as_markup()

    return node_keyboard.as_markup(resize_keyboard=True)
