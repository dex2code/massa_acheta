from loguru import logger

import asyncio
from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from quickchart import QuickChart
from datetime import datetime

import app_globals


router = Router()


@router.message(StateFilter(None), Command("massa_chart"))
@logger.catch
async def cmd_massa_chart(message: Message) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from user '{message.from_user.id}' in chat '{message.chat.id}'")

    stakers_chart_config = {
        "type": "line",
        "options": {
            "title": {
                "display": True,
                "text": "MASSA Mainnet stakers"
            }
        },
        "data": {
            "labels": [],
            "datasets": [
                {
                    "label": "Active stakers",
                    "data": [],
                    "fill": False,
                    "borderColor": "blue",
                    "borderWidth": 2
                }
            ]
        }
    }

    rolls_chart_config = {
        "type": "line",
        "options": {
            "title": {
                "display": True,
                "text": "MASSA Mainnet staked Rolls"
            }
        },
        "data": {
            "labels": [],
            "datasets": [
                {
                    "label": "Rolls staked",
                    "data": [],
                    "fill": False,
                    "borderColor": "red",
                    "borderWidth": 2
                }
            ]
        }
    }

    rewards_chart_config = {
        "type": "line",
        "options": {
            "title": {
                "display": True,
                "text": "MASSA Mainnet estimated rewards (100 Rolls staked)"
            }
        },
        "data": {
            "labels": [],
            "datasets": [
                {
                    "label": "MAS earned for 100 staked Rolls",
                    "data": [],
                    "fill": False,
                    "borderColor": "green",
                    "borderWidth": 2
                }
            ]
        }
    }


    for measure in app_globals.massa_network['stat']:

        label = measure['time']
        label = datetime.utcfromtimestamp(label).strftime("%b, %-d")
        stakers = measure['stakers']
        rolls = measure['rolls']
        rewards = measure['rewards']

        stakers_chart_config['data']['labels'].append(label)
        stakers_chart_config['data']['datasets'][0]['data'].append(stakers)

        rolls_chart_config['data']['labels'].append(label)
        rolls_chart_config['data']['datasets'][0]['data'].append(rolls)

        rewards_chart_config['data']['labels'].append(label)
        rewards_chart_config['data']['datasets'][0]['data'].append(rewards)

    stakers_chart = QuickChart()
    stakers_chart.device_pixel_ratio = 2.0
    stakers_chart.width = 600
    stakers_chart.height = 300
    stakers_chart.config = stakers_chart_config
    stakers_chart_url = stakers_chart.get_url()

    rolls_chart = QuickChart()
    rolls_chart.device_pixel_ratio = 2.0
    rolls_chart.width = 600
    rolls_chart.height = 300
    rolls_chart.config = rolls_chart_config
    rolls_chart_url = rolls_chart.get_url()

    rewards_chart = QuickChart()
    rewards_chart.device_pixel_ratio = 2.0
    rewards_chart.width = 600
    rewards_chart.height = 300
    rewards_chart.config = rewards_chart_config
    rewards_chart_url = rewards_chart.get_url()


    try:
        await message.answer_photo(
            photo=stakers_chart_url,
            caption="Active stakers chart",
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )
        await asyncio.sleep(delay=0.5)

        await message.answer_photo(
            photo=rolls_chart_url,
            caption="Rolls staked chart",
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )
        await asyncio.sleep(delay=0.5)

        await message.answer_photo(
            photo=rewards_chart_url,
            caption="Estimated earnings chart",
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )
        await asyncio.sleep(delay=0.5)

    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    return
