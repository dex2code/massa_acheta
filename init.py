import json
from pathlib import Path
from sys import exit as sys_exit
from loguru import logger

from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode




settings_path = ".settings.json"
settings_obj = Path(settings_path)



app_settings = {}

if not settings_obj.exists():
    logger.critical(f"No settings file '{settings_obj}' exists.")
    sys_exit(1)
else:
    logger.info(f"Loading settings from existing '{settings_obj}' file")


with open(file=settings_obj, mode="r") as input_settings:

    try:
        app_settings = json.load(fp=input_settings)

    except Exception as E:
        logger.critical(f"Cannot load settings from '{settings_obj}': ({str(E)})")
        sys_exit(1)

    else:
        logger.info(f"Successfully loaded settings from '{settings_obj}' file!")




tg_dp = Dispatcher()
tg_bot = Bot(token=app_settings['telegram']['key'], parse_mode=ParseMode.HTML)




if __name__ == "__main__":
    pass
