from loguru import logger

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.utils.formatting import as_list, as_line
from aiogram.enums import ParseMode
from quickchart import QuickChart
from datetime import datetime

import app_globals


router = Router()


@router.message(StateFilter(None), Command("massa_chart"))
@logger.catch
async def cmd_massa_chart(message: Message) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from user '{message.from_user.id}' in chat '{message.chat.id}'")

    chart_config = {

        "type": "line",

        "options": {
            "staked": False,

            "title": {
                "display": True,
                "text": "MASSA Mainnet chart"
            },

            "scales": {
                "yAxes": [
                    {
                        "id": "rolls",
                        "type": "linear",
                        "display": True,
                        "position": "left"
                    },
                    {
                        "id": "stakers",
                        "type": "linear",
                        "display": True,
                        "position": "right",
                        "gridLines": {
                            "drawOnChartArea": False
                        },
                        "ticks": {
                            "min": 0,
                            "max": 0
                        }
                    }
                ]
            }
        },

        "data": {
            "labels": [],

            "datasets": [
                {
                    "label": "Rolls staked",
                    "fill": False,
                    "borderColor": "blue",
                    "borderWidth": 2,
                    "data": [],
                    "yAxisID": "rolls"
                },
                {
                    "label": "Active stakers",
                    "fill": False,
                    "borderColor": "red",
                    "borderWidth": 2,
                    "data": [],
                    "yAxisID": "stakers"
                }
            ]
        }
    }

    try:
        for measure in app_globals.massa_network['stat']:

            label = measure['time']
            label = datetime.utcfromtimestamp(label).strftime("%b, %-d")

            rolls = measure['rolls']
            stakers = measure['stakers']

            chart_config['data']['labels'].append(label)
            chart_config['data']['datasets'][0]['data'].append(rolls)
            chart_config['data']['datasets'][1]['data'].append(stakers)

            min_stakers = min(chart_config['data']['datasets'][1]['data'])
            min_stakers = int(min_stakers * 0.95)
            max_stakers = max(chart_config['data']['datasets'][1]['data'])
            max_stakers = int(max_stakers * 1.2)
            chart_config['options']['scales']['yAxes'][1]['ticks']['min'] = min_stakers
            chart_config['options']['scales']['yAxes'][1]['ticks']['max'] = max_stakers

        chart = QuickChart()
        chart.device_pixel_ratio = 2.0
        chart.width = 600
        chart.height = 300
        chart.config = chart_config
        chart_url = chart.get_url()

    except BaseException as E:
        logger.error(f"Cannot prepare MASSA Mainnet chart ({str(E)})")
        t = as_list(
            as_line("🤷 Charts are temporary unavailable. Try later."),
            as_line("☝ Use help to learn bot commands")
        )
        try:
            await message.reply(
                text=t.as_html(),
                parse_mode=ParseMode.HTML,
                request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
            )
        except BaseException as E:
            logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    else:
        try:
            await message.reply_photo(
                photo=chart_url,
                parse_mode=ParseMode.HTML,
                request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
            )
        except BaseException as E:
            logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    return
