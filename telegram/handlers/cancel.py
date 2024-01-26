from loguru import logger

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import as_list

from app_globals import app_config, bot


router = Router()


@router.message(Command("cancel"))
@logger.catch
async def cmd_cancel(message: Message, state: FSMContext):
    logger.debug("-> Enter Def")
    if message.chat.id != bot.chat_id: return

    await state.set_data({})
    await state.clear()

    t = as_list(
        app_config['telegram']['service_nickname'], "",
        "❌ Action cancelled!"
    )
    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove(),
        request_timeout=app_config['telegram']['sending_timeout_sec']
    )
