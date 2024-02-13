from loguru import logger

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils.formatting import as_list
from time import time as t_now

import app_globals

from tools import get_last_seen

router = Router()


@router.message(Command("massa_info"))
@logger.catch
async def cmd_massa_info(message: Message) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from user '{message.chat.id}'")

    computed_rewards = ""
    my_contribution = app_globals.massa_network_values['total_staked_rolls'] / 100
    my_blocks = 172_800 / my_contribution
    my_reward = round(
        my_blocks * app_globals.massa_network_values['block_reward'],
        2
    )
    computed_rewards = f"🪙 MAX rewards for 100 Rolls: {my_reward:,} MAS / day"

    info_last_update = get_last_seen(
        last_time=app_globals.massa_network_values['last_updated'],
        current_time=t_now()
    )
    t = as_list(
        f"📚 MASSA network info:", "",
        f"💾 Latest released MASSA version: \"{app_globals.massa_network_values['latest_release']}\"",
        f"🏃 Current MASSA release: \"{app_globals.massa_network_values['current_release']}\"", "",
        f"🌀 Current cycle: {app_globals.massa_network_values['current_cycle']}", "",
        f"🪙 Roll price: {app_globals.massa_network_values['roll_price']:,} MAS",
        f"💰 Block reward: {app_globals.massa_network_values['block_reward']} MAS", "",
        f"👥 Total stakers: {app_globals.massa_network_values['total_stakers']:,}",
        f"🗞 Total staked rolls: {app_globals.massa_network_values['total_staked_rolls']:,}", "",
        computed_rewards, "",
        f"👁 Info updated: {info_last_update}", "",
        f"☝ Service checks updates: every {app_globals.app_config['service']['massa_network_update_period_mins']} mins"
    )
    await message.reply(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    return
