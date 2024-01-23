from loguru import logger

import asyncio
import json

from app_globals import app_results, app_config
from remotes.node import check_node
from remotes.wallet import check_wallet


@logger.catch
async def monitor() -> None:
    logger.debug(f"-> Enter Def")

    while True:

        node_coros = set()
        wallet_coros = set()


        for node_name in app_results:
            node_coros.add(check_node(node_name=node_name))

            for wallet_addr in app_results[node_name]['wallets']:
                wallet_coros.add(check_wallet(node_name=node_name, wallet_addr=wallet_addr))

        await asyncio.gather(*node_coros)
        await asyncio.gather(*wallet_coros)

        logger.debug(f"Current app_results:\n{json.dumps(obj=app_results, indent=4)}")

        logger.info(f"Sleeping for {app_config['service']['main_loop_period_sec']} seconds...")
        await asyncio.sleep(delay=app_config['service']['main_loop_period_sec'])




if __name__ == "__main__":
    pass
