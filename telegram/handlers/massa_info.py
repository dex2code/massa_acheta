from loguru import logger

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils.formatting import as_list

from app_config import app_config
import app_globals

from tools import get_last_seen, get_rewards_mas_day


router = Router()


@router.message(StateFilter(None), Command("massa_info"))
@logger.catch
async def cmd_massa_info(message: Message) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from '{message.from_user.id}'@'{message.chat.id}'")

    wallet_computed_rewards = await get_rewards_mas_day(rolls_number=100)

    info_last_update = await get_last_seen(
        last_time=app_globals.massa_network['values']['last_updated']
    )
    t = as_list(
        f"💾 Latest released MASSA version: \"{app_globals.massa_network['values']['latest_release']}\"",
        f"🏃 Current MASSA release: \"{app_globals.massa_network['values']['current_release']}\"", "",
        f"🌀 Current cycle: {app_globals.massa_network['values']['current_cycle']}", "",
        f"🗞 Roll price: {app_globals.massa_network['values']['roll_price']:,} MAS",
        f"💰 Block reward: {app_globals.massa_network['values']['block_reward']} MAS", "",
        f"👥 Total stakers: {app_globals.massa_network['values']['total_stakers']:,}",
        f"🗞 Total staked rolls: {app_globals.massa_network['values']['total_staked_rolls']:,}", "",
        f"🪙 Estimated earnings for 100 Rolls ≈ {wallet_computed_rewards:,} MAS / Day", "",
        f"👁 Info updated: {info_last_update}", "",
        f"☝ Service checks updates: every {app_config['service']['massa_network_update_period_min']} mins"
    )
    try:
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_config['telegram']['sending_timeout_sec']
        )
    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    return
