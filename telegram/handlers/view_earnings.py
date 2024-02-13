from loguru import logger

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils.formatting import as_list, as_line, Underline, TextLink
from time import time as t_now

import app_globals

from tools import get_last_seen


router = Router()


@router.message(Command("view_earnings"))
@logger.catch
async def cmd_view_earnings(message: Message) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from user '{message.from_user.id}' in chat '{message.chat.id}'")

    message_list = message.text.split()

    if len(message_list) < 2:
        t = as_list(
            "❓ No Rolls number provided", "",
            as_line(
                "☝ Try /view_earnings ",
                Underline("Rolls_number"),
                " command"
            )
        )
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )

        return
    
    rolls_number = message_list[1]

    try:
        rolls_number = int(rolls_number)
        if rolls_number < 0 or rolls_number > app_globals.massa_network_values['total_staked_rolls']:
            raise Exception
    except BaseException:
        t = as_list(
            "‼ Wrong Rolls number value", "",
            as_line(
                "☝ Try /view_earnings ",
                Underline("Rolls_number"),
                " command"
            )
        )
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )

        return

    my_contribution = app_globals.massa_network_values['total_staked_rolls'] / rolls_number
    my_blocks = 172_800 / my_contribution
    my_reward = round(
        my_blocks * app_globals.massa_network_values['block_reward'],
        2
    )

    massa_updated = get_last_seen(
        last_time=app_globals.massa_network_values['last_updated'],
        current_time=t_now()
    )

    my_percentage = round(
        (rolls_number / app_globals.massa_network_values['total_staked_rolls']) * 100,
        6
    )

    t = as_list(
        f"🏦 Total number of staked Rolls in MASSA Mainnet: {app_globals.massa_network_values['total_staked_rolls']:,} (updated: {massa_updated})", "",
        f"🍰 Your contribution is: {rolls_number} Rolls ({my_percentage}%)", "",
        f"🪙 Your theoretically MAX earnings: {my_reward} MAS / day", "",
        as_line(
            "👉 ",
            TextLink(
                "More info here",
                url="https://docs.massa.net/docs/learn/tokenomics#example-how-to-compute-my-expected-staking-rewards-"
            )
        )
    )
    await message.reply(
    text=t.as_html(),
    parse_mode=ParseMode.HTML,
    request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
)
