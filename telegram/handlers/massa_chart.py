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

            "title": {
                "display": True,
                "text": "MASSA Mainnet chart"
            },

            "scales": {
                "yAxes": [
                    {
                        "id": "stakers",
                        "display": True,
                        "position": "left",
                        "ticks": { "fontColor": "green" },
                        "gridLines": { "drawOnChartArea": False }
                    },
                    {
                        "id": "rolls",
                        "display": True,
                        "position": "right",
                        "ticks": { "fontColor": "red" },
                        "gridLines": { "drawOnChartArea": False }
                    }
                ]
            }
        },

        "data": {
            "labels": [],

            "datasets": [
                {
                    "label": "Active stakers",
                    "yAxisID": "stakers",
                    "lineTension": 0.4,
                    "fill": False,
                    "borderColor": "green",
                    "borderWidth": 1,
                    "pointRadius": 0,
                    "data": []
                },
                {
                    "label": "Rolls staked",
                    "yAxisID": "rolls",
                    "lineTension": 0.4,
                    "fill": False,
                    "borderColor": "red",
                    "borderWidth": 2,
                    "pointRadius": 0,
                    "data": []
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
            chart_config['data']['datasets'][0]['data'].append(stakers)
            chart_config['data']['datasets'][1]['data'].append(rolls)

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
            as_line("☝ Use /help to learn bot commands")
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
