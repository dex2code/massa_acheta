import asyncio
import json

from loguru import logger
from init import app_settings
from tools import pull_node_api, send_telegram_message
from time import time as t_now
from node import check_node
from wallet import check_wallet



@logger.catch
async def monitor() -> None:
    logger.debug(f"-> Enter def")

    while True:

        node_coros = set()
        wallet_coros = set()

        for node_name in app_settings['nodes']:
            node_coros.add(check_node(node_name=node_name))

            for wallet_addr in app_settings['nodes'][node_name]['wallets']:
                wallet_coros.add(check_wallet(node_name=node_name, wallet_addr=wallet_addr))

        await asyncio.gather(*node_coros)
        await asyncio.gather(*wallet_coros)

        logger.debug(f"Current app_settings:\n{json.dumps(obj=app_settings, indent=4)}")

        logger.info(f"Sleeping for {app_settings['loop_timeout_seconds']} seconds...")
        await asyncio.sleep(delay=app_settings['loop_timeout_seconds'])




if __name__ == "__main__":
    pass
