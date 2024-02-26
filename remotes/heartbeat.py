from loguru import logger

import asyncio
from aiogram.utils.formatting import as_list, as_line, TextLink

from app_config import app_config
import app_globals

from telegram.queue import queue_telegram_message
from tools import get_last_seen, get_short_address, get_rewards_mas_day, save_public_dir


async def heartbeat() -> None:
    logger.debug(f"-> Enter Def")

    try:
        while True:
            logger.info(f"Sleeping for {app_config['service']['heartbeat_period_hours'] * 60 * 60} seconds...")
            await asyncio.sleep(delay=(app_config['service']['heartbeat_period_hours'] * 60 * 60))
            logger.info(f"Heartbeat planner shedule time")

            computed_rewards = await get_rewards_mas_day(rolls_number=100)

            heartbeat_list = []
            heartbeat_list.append(
                as_list(
                    "📚 MASSA network info:",
                    f" 👥 Total stakers: {app_globals.massa_network['values']['total_stakers']:,}",
                    f" 🗞 Total staked rolls: {app_globals.massa_network['values']['total_staked_rolls']:,}",
                    f"🪙 Estimated rewards for 100 Rolls ≈ {computed_rewards:,} MAS / Day",
                    f"👁 Info updated: {await get_last_seen(last_time=app_globals.massa_network['values']['last_updated'])}", ""
                )
            )

            if len(app_globals.app_results) == 0:
                heartbeat_list.append("⭕ Node list is empty\n")

            else:
                for node_name in app_globals.app_results:
                    heartbeat_list.append(f"🏠 Node: \"{node_name}\"")
                    heartbeat_list.append(f"📍 {app_globals.app_results[node_name]['url']}")

                    last_seen = await get_last_seen(
                        last_time=app_globals.app_results[node_name]['last_update']
                    )

                    if app_globals.app_results[node_name]['last_status'] == True:
                        heartbeat_list.append(f"🌿 Status: Online ({last_seen})")

                        num_wallets = len(app_globals.app_results[node_name]['wallets'])
                        if num_wallets == 0:
                            heartbeat_list.append("⭕ No wallets attached\n")
                        else:
                            heartbeat_list.append(f"👛 {num_wallets} wallet(s) attached:")

                            wallet_list = []

                            for wallet_address in app_globals.app_results[node_name]['wallets']:

                                if app_globals.app_results[node_name]['wallets'][wallet_address]['last_status'] == True:
                                    wallet_list.append(
                                        as_line(
                                            "⦙\n",
                                            "⦙… ",
                                            TextLink(
                                                await get_short_address(address=wallet_address),
                                                url=f"{app_config['service']['mainnet_explorer_url']}/address/{wallet_address}"
                                            ),
                                            f" ( {app_globals.app_results[node_name]['wallets'][wallet_address]['final_balance']:,} MAS )",
                                            end=""
                                        )
                                    )
                                else:
                                    wallet_list.append(
                                        as_line(
                                            "⦙\n",
                                            "⦙… ",
                                            TextLink(
                                                await get_short_address(address=wallet_address),
                                                url=f"{app_config['service']['mainnet_explorer_url']}/address/{wallet_address}"
                                            ),
                                            " ( ? MAS )",
                                            end=""
                                        )
                                    )
                            
                            heartbeat_list.append(as_list(*wallet_list))

                    else:
                        heartbeat_list.append(f"☠️ Status: Offline ({last_seen})")
                        heartbeat_list.append("⭕ No wallets info available")

                    heartbeat_list.append("")

            t = as_list(
                "💓 Heartbeat message:", "",
                *heartbeat_list,
                f"⏳ Heartbeat schedule: every {app_config['service']['heartbeat_period_hours']} hour(s)"
            )
            await queue_telegram_message(message_text=t.as_html())

            save_public_dir()

    except BaseException as E:
        logger.error(f"Exception {str(E)} ({E})")
    
    finally:
        logger.error(f"<- Quit Def")

    return




if __name__ == "__main__":
    pass
