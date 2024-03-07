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
from time import time

from app_config import app_config

from tools import save_app_results


### Set start time ###
acheta_start_time = int(
    time()
)



### Global mutex ###
results_lock = asyncio.Lock()



### Init results ###
app_results = {}

app_results_obj = Path(app_config['service']['results_path'])
if app_results_obj.exists():
    logger.info(f"Loading results from '{app_results_obj}' file...")

    with open(file=app_results_obj, mode="rt") as input_results:
        try:
            app_results = json.load(fp=input_results)

        except BaseException as E:
            logger.critical(f"Cannot load results from '{app_results_obj}' ({str(E)})")
            sys_exit(1)

        else:
            logger.info(f"Successfully loaded results from '{app_results_obj}' file!")

else:
    logger.warning(f"No results file '{app_results_obj}' exists. Trying to create...")

    try:
        if not save_app_results():
            raise Exception

    except BaseException as E:
        logger.critical(f"Cannot create '{app_results_obj}' file. Exiting...")
        sys_exit(1)

    else:
        logger.info(f"Successfully created empty '{app_results_obj}' file")

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
                24 * 60 / app_config['service']['main_loop_period_min']
            )
        )



### MASSA network values ###
massa_config = {}
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
        24 * 60 / app_config['service']['massa_network_update_period_min']
    )
)



### Restore stat values ###
app_stat_obj = Path(app_config['service']['stat_path'])
if app_stat_obj.exists():
    logger.info(f"Loading stat from '{app_stat_obj}' file...")

    try:
        with open(file=app_stat_obj, mode="rt") as input_stat:
            app_stat = json.load(fp=input_stat)

    except BaseException as E:
        logger.error(f"Cannot load stat from '{app_stat_obj}': ({str(E)})")

    else:
        logger.info(f"Loaded app_stat from '{app_stat_obj}' successfully")

        try:
            for node_name in app_results:
                for wallet_address in app_results[node_name]['wallets']:
                    wallet_stat = app_stat['app_results'][node_name][wallet_address].get("stat", None)
                    if wallet_stat and type(wallet_stat) == list and len(wallet_stat) > 0:
                        for measure in wallet_stat:
                            app_results[node_name]['wallets'][wallet_address]['stat'].append(measure)
                    logger.info(f"Restored {len(app_results[node_name]['wallets'][wallet_address]['stat'])} measures for wallet '{wallet_address}'@'{node_name}'")
        
        except BaseException as E:
            logger.error(f"Cannot restore app_result stat ({str(E)})")
        
        else:
            logger.info(f"Restored app_results stat successfully")

        try:
            massa_network_stat = app_stat['massa_network'].get("stat", None)
            if massa_network_stat and type(massa_network_stat) == list and len(massa_network_stat) > 0:
                for measure in massa_network_stat:
                    if type(measure) == dict:
                        massa_network['stat'].append(measure)
            logger.info(f"Restored {len(massa_network['stat'])} measures for massa_network")
        
        except BaseException as E:
            logger.error(f"Cannot restore massa_network stat ({str(E)})")
        
        else:
            logger.info(f"Restored massa_network stat successfully")



### Init Telegram stuff ###
class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8'
    )

    ACHETA_KEY: SecretStr
    ACHETA_CHAT: int

bot = BotSettings()

telegram_queue = deque()
tg_dp = Dispatcher(
    storage=MemoryStorage()
)
tg_bot = Bot(
    token=bot.ACHETA_KEY.get_secret_value(),
    parse_mode=ParseMode.HTML,
    disable_web_page_preview=True
)



### Acheta releases stuff ###
local_acheta_release = "ACHETA.1.2.3"
latest_acheta_release = ""



### Init deferred_credits ###
deferred_credits = {}

deferred_credits_obj = Path(app_config['service']['deferred_credits_path'])

if not deferred_credits_obj.exists():
    logger.warning(f"No deferred_credits file '{deferred_credits_obj}' exists. Skipping...")

else:
    logger.info(f"Loading deferred_credits from '{deferred_credits_obj}' file...")

    with open(file=deferred_credits_obj, mode="rt") as input_deferred_credits:
        try:
            deferred_credits = json.load(fp=input_deferred_credits)

        except BaseException as E:
            logger.error(f"Cannot load deferred_credits from '{deferred_credits_obj}' ({str(E)})")

        else:
            logger.info(f"Successfully loaded deferred_credits from '{deferred_credits_obj}' file!")



### Init public_user_dir ###
public_dir = {}

public_dir_obj = Path(app_config['service']['public_dir_path'])

if not public_dir_obj.exists():
    logger.warning(f"No public_dir file '{public_dir_obj}' exists. Skipping...")

else:
    logger.info(f"Loading public_dir from '{public_dir_obj}' file...")

    with open(file=public_dir_obj, mode="rt") as input_public_dir:
        try:
            public_dir = json.load(fp=input_public_dir)
        
        except BaseException as E:
            logger.error(f"Cannot load public_dir from '{public_dir_obj}' file ({str(E)})")
        
        else:
            logger.info(f"Successfully loaded public_dir from '{public_dir_obj}' file ({len(public_dir)} keys)")





if __name__ == "__main__":
    pass
