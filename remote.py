import asyncio
import json
from loguru import logger
from app_init import app_results, app_config
from node import check_node
from wallet import check_wallet
from tools import save_results



@logger.catch
async def monitor() -> None:
    logger.debug(f"-> Enter def")

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
        await save_results()

        logger.info(f"Sleeping for {app_config['service']['loop_timeout_sec']} seconds...")
        await asyncio.sleep(delay=app_config['service']['loop_timeout_sec'])






if __name__ == "__main__":
    pass
