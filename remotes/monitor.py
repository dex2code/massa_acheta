from loguru import logger

import asyncio

from app_config import app_config
import app_globals

from remotes.node import check_node
from remotes.wallet import check_wallet
from remotes.releases import check_releases


@logger.catch
async def monitor() -> None:
    logger.debug(f"-> Enter Def")

    try:
        while True:
            node_coros = set()
            wallet_coros = set()

            for node_name in app_globals.app_results:
                node_coros.add(check_node(node_name=node_name))

                for wallet_address in app_globals.app_results[node_name]['wallets']:
                    wallet_coros.add(check_wallet(node_name=node_name, wallet_address=wallet_address))

            async with app_globals.results_lock:
                await asyncio.gather(*node_coros)
                await asyncio.gather(*wallet_coros)

            await asyncio.gather(check_releases())

            logger.info(f"Sleeping for {app_config['service']['main_loop_period_min']} minutes...")
            await asyncio.sleep(
                delay=(app_config['service']['main_loop_period_min'] * 60)
            )

    except BaseException as E:
        logger.error(f"Exception {str(E)} ({E})")
    
    finally:
        logger.error(f"<- Quit Def")

    return




if __name__ == "__main__":
    pass
