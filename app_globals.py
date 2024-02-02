from loguru import logger

import json
import asyncio
from pathlib import Path
from sys import exit as sys_exit
from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from collections import deque
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

from app_config import app_config


'''
Init results
'''
results_obj = Path(app_config['service']['results_path'])

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



'''
Init Telegram stuff
'''
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

    ACHETA_KEY: SecretStr
    ACHETA_CHAT: int

bot = Settings()


telegram_queue = deque()
tg_dp = Dispatcher(storage=MemoryStorage())
tg_bot = Bot(token=bot.ACHETA_KEY.get_secret_value(), disable_web_page_preview=True, parse_mode=ParseMode.HTML)



'''
Releases stuff
'''
latest_massa_release = ""
local_acheta_release = "ACHETA.1.0.0"
latest_acheta_release = ""



'''
Global mutex
'''
results_lock = asyncio.Lock()


if __name__ == "__main__":
    pass
