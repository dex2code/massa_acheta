from loguru import logger

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from quickchart import QuickChart
from datetime import datetime

import app_globals


router = Router()


@router.message(StateFilter(None), Command("massa_stat"))
@logger.catch
async def cmd_massa_stat(message: Message) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from user '{message.from_user.id}' in chat '{message.chat.id}'")

    chart_config = {
        "type": "line",
        "options": {
            "title": {
                "display": True,
                "text": "MASSA Mainnet chart"
            }
        },
        "data": {
            "labels": [],
            "datasets": [
                {
                    "label": "Stakers",
                    "data": [],
                    "fill": False,
                    "borderColor": "green",
                    "borderWidth": 1
                },
                {
                    "label": "Rolls",
                    "data": [],
                    "fill": False,
                    "borderColor": "red",
                    "borderWidth": 1
                }
            ]
        }
    }

    for measure in app_globals.massa_network['stat']:

        label = measure['time']
        label = datetime.utcfromtimestamp(label).strftime("%b, %-d")
        stakers = measure['stakers']
        rolls = measure['rolls']

        chart_config['data']['labels'].append(label)
        chart_config['data']['datasets'][0]['data'].append(stakers)
        chart_config['data']['datasets'][1]['data'].append(rolls)

    chart = QuickChart()
    chart.config = chart_config
    chart_url = chart.get_url()

    try:
        await message.reply_photo(
            photo=chart_url,
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )
    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    return
