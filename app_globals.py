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
app_results = {}

results_obj = Path(app_config['service']['results_path'])

if not results_obj.exists():
    logger.warning(f"No results file '{results_obj}' exists. Trying to create...")

    try:
        with open(results_obj, "w") as new_results:
            new_results.write(json.dumps(app_results))
            new_results.flush()
    
    except BaseException as E:
        logger.critical(f"Cannot create '{results_obj}' file. Exiting...")
        sys_exit(1)

    else:
        logger.info(f"Successfully created '{results_obj}' file")

else:
    logger.info(f"Loading results from '{results_obj}' file...")


with open(file=results_obj, mode="r") as input_results:
    try:
        app_results = json.load(fp=input_results)

    except BaseException as E:
        logger.critical(f"Cannot load results from '{results_obj}': ({str(E)})")
        sys_exit(1)

    else:
        logger.info(f"Successfully loaded results from '{results_obj}' file!")


for node_name in app_results:
    app_results[node_name]['last_status'] = "unknown"
    app_results[node_name]['last_update'] = 0
    app_results[node_name]['last_result'] = {"unknown": "Never updated before"}

    for wallet_address in app_results[node_name]['wallets']:
        app_results[node_name]['wallets'][wallet_address] = {}
        app_results[node_name]['wallets'][wallet_address]['final_balance'] = 0
        app_results[node_name]['wallets'][wallet_address]['candidate_rolls'] = 0
        app_results[node_name]['wallets'][wallet_address]['active_rolls'] = 0
        app_results[node_name]['wallets'][wallet_address]['missed_blocks'] = 0
        app_results[node_name]['wallets'][wallet_address]['last_status'] = "unknown"
        app_results[node_name]['wallets'][wallet_address]['last_update'] = 0
        app_results[node_name]['wallets'][wallet_address]['last_result'] = {"unknown": "Never updated before"}



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
Acheta releases stuff
'''
local_acheta_release = "ACHETA.1.0.3"
latest_acheta_release = ""



'''
Global mutex
'''
results_lock = asyncio.Lock()



'''
MASSA network values
'''
massa_network_values =  {
    "latest_release": "",
    "current_release": "",
    "roll_price": 0,
    "block_reward": 0,
    "total_stakers": 0,
    "total_staked_rolls": 0
}



if __name__ == "__main__":
    pass
