from loguru import logger

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils.formatting import as_list

import app_globals


router = Router()


@router.message(Command("massa_info"))
@logger.catch
async def cmd_massa_info(message: Message) -> None:
    logger.debug("-> Enter Def")

    t = as_list(
        f"📚 MASSA network info:", "",
        f"💾 Latest released MASSA version: \"{app_globals.massa_network_values['latest_release']}\"",
        f"🏃 Current MASSA release: \"{app_globals.massa_network_values['current_release']}\"", "",
        f"🪙 Roll price: {app_globals.massa_network_values['roll_price']:,} MAS",
        f"💰 Block reward: {app_globals.massa_network_values['block_reward']} MAS", "",
        f"👥 Total stakers: {app_globals.massa_network_values['total_stakers']:,}",
        f"🗞 Total staked rolls: {app_globals.massa_network_values['total_staked_rolls']:,}", "",
        f"☝ Service checks updates: every {app_globals.app_config['service']['massa_network_update_period_hours']} hour(s)"

    )
    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
    )

    return
