from loguru import logger

import json
import asyncio
import pickle
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

from tools import save_app_results

acheta_start_time = 0

'''
Init results
'''
app_results_pickle = False
app_results_obj = Path(f"{app_config['service']['results_path']}.bin")

if app_results_obj.exists():
    logger.info(f"Found '{app_results_obj}' file. Trying to load app_results state...")

    try:
        with open(file=app_results_obj, mode="rb") as app_results_source_pickle:
            app_results_source_pickle.seek(0)
            app_results = pickle.load(file=app_results_source_pickle)
    
    except BaseException as E:
        logger.error(f"Cannot load '{app_results_obj}' file ({str(E)}). Loading app_results from JSON...")
    
    else:
        logger.info(f"app_results state loaded from '{app_results_obj}' file successfully")
        app_results_pickle = True

if not app_results_pickle:
    app_results = {}

    app_results_obj = Path(app_config['service']['results_path'])

    if not app_results_obj.exists():
        logger.warning(f"No results file '{app_results_obj}' exists. Trying to create...")

        try:
            if not save_app_results():
                raise Exception

        except BaseException as E:
            logger.critical(f"Cannot create '{app_results_obj}' file. Exiting...")
            sys_exit(1)

        else:
            logger.info(f"Successfully created empty '{app_results_obj}' file")

    else:
        logger.info(f"Loading results from '{app_results_obj}' file...")

        with open(file=app_results_obj, mode="rt") as input_results:
            try:
                app_results = json.load(fp=input_results)

            except BaseException as E:
                logger.critical(f"Cannot load results from '{app_results_obj}': ({str(E)})")
                sys_exit(1)

            else:
                logger.info(f"Successfully loaded results from '{app_results_obj}' file!")


    for node_name in app_results:
        app_results[node_name]['last_status'] = "unknown"
        app_results[node_name]['last_update'] = 0
        app_results[node_name]['last_chain_id'] = 0
        app_results[node_name]['last_cycle'] = 0
        app_results[node_name]['last_result'] = {"unknown": "Never updated before"}

        for wallet_address in app_results[node_name]['wallets']:
            app_results[node_name]['wallets'][wallet_address] = {}
            app_results[node_name]['wallets'][wallet_address]['last_status'] = "unknown"
            app_results[node_name]['wallets'][wallet_address]['last_update'] = 0
            app_results[node_name]['wallets'][wallet_address]['final_balance'] = 0
            app_results[node_name]['wallets'][wallet_address]['candidate_rolls'] = 0
            app_results[node_name]['wallets'][wallet_address]['active_rolls'] = 0
            app_results[node_name]['wallets'][wallet_address]['missed_blocks'] = 0
            app_results[node_name]['wallets'][wallet_address]['last_result'] = {"unknown": "Never updated before"}
            app_results[node_name]['wallets'][wallet_address]['stat'] = deque(
                maxlen=int(
                    app_config['service']['wallet_stat_keep_days'] * 24 * 60 / app_config['service']['main_loop_period_min']
                )
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
massa_network_pickle = False
massa_network_obj = Path(f"{app_config['service']['massa_network_path']}.bin")
if massa_network_obj.exists():
    logger.info(f"Found '{massa_network_obj}' file. Trying to load MASSA state...")

    try:
        with open(file=massa_network_obj, mode="rb") as massa_network_source_pickle:
            massa_network_source_pickle.seek(0)
            massa_network = pickle.load(file=massa_network_source_pickle)
    
    except BaseException as E:
        logger.error(f"Cannot load '{massa_network_obj}' file ({str(E)}) Loading empty MASSA state...")
    
    else:
        logger.info(f"MASSA state loaded from '{massa_network_obj}' file successfully (found {len(massa_network['stat'])} measures)")
        massa_network_pickle = True

if not massa_network_pickle:
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
