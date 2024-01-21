import json
from pathlib import Path
from sys import exit as sys_exit
from loguru import logger

from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode

from collections import deque

telegram_queue = deque()


from dev_config import *
# from app_config import *

app_config = {}
app_config['telegram'] = telegram
app_config['service'] = service

results_path = "dev_results.json"
#results_path = "app_results.json"

results_obj = Path(results_path)


app_results = {}

if not results_obj.exists():
    logger.critical(f"No results file '{results_obj}' exists.")
    sys_exit(1)
else:
    logger.info(f"Loading results from existing '{results_obj}' file...")


with open(file=results_obj, mode="r") as input_results:

    try:
        app_results = json.load(fp=input_results)

    except Exception as E:
        logger.critical(f"Cannot load results from '{results_obj}': ({str(E)})")
        sys_exit(1)

    else:
        logger.info(f"Successfully loaded results from '{results_obj}' file!")


tg_dp = Dispatcher()
tg_bot = Bot(token=telegram['key'], parse_mode=ParseMode.HTML)


if __name__ == "__main__":
    pass
