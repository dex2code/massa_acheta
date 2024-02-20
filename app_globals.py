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
from collections import deque

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
    app_results[node_name]['last_chain_id'] = 0
    app_results[node_name]['last_cycle'] = 0
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
        app_results[node_name]['wallets'][wallet_address]['stat'] = deque(
            maxlen=app_config['service']['wallet_stat_keep_days'] * 24 * 60 / app_config['service']['main_loop_period_min']
        )


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
local_acheta_release = "ACHETA.1.0.9"
latest_acheta_release = ""



'''
Global mutex
'''
results_lock = asyncio.Lock()



'''
MASSA network values
'''
massa_network = {}
massa_network['values'] =  {
    "latest_release": "",
    "current_release": "",
    "current_cycle": 0,
    "roll_price": 0,
    "block_reward": 0,
    "total_stakers": 0,
    "total_staked_rolls": 0,
    "last_updated": 0
}
massa_network['stat'] = deque(
    maxlen=int(
        app_config['service']['massa_network_stat_keep_days'] * 24 * 60 / app_config['service']['massa_network_update_period_min']
    )
)


'''
Init deferred_credits
'''
deferred_credits = {}

deferred_credits_obj = Path(app_config['service']['deferred_credits_path'])

if not deferred_credits_obj.exists():
    logger.error(f"No deferred_credits file '{deferred_credits_obj}' exists. Skipping...")

else:
    logger.info(f"Loading deferred_credits from '{deferred_credits_obj}' file...")

    with open(file=deferred_credits_obj, mode="r") as input_deferred_credits:
        try:
            deferred_credits = json.load(fp=input_deferred_credits)

        except BaseException as E:
            logger.error(f"Cannot load deferred_credits from '{deferred_credits_obj}': ({str(E)})")

        else:
            logger.info(f"Successfully loaded deferred_credits from '{deferred_credits_obj}' file!")




if __name__ == "__main__":
    pass
