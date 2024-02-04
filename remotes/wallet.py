from loguru import logger

import json
from time import time as t_now
from aiogram.utils.formatting import as_list, as_line, Code, TextLink

import app_globals
from telegram.queue import queue_telegram_message
from tools import pull_node_api, get_short_address


@logger.catch
async def check_wallet(node_name: str="", wallet_address: str="") -> None:
    logger.debug(f"-> Enter Def")

    if app_globals.app_results[node_name]['last_status'] != True:
        logger.warning(f"Will not watch wallet '{wallet_address}' on node '{node_name}' because of its offline")
        app_globals.app_results[node_name]['wallets'][wallet_address]['last_status'] = False
        app_globals.app_results[node_name]['wallets'][wallet_address]['last_result'] = {"error": "Host node is offline"}
        return

    payload =   json.dumps(
                    {
                        "id": 0,
                        "jsonrpc": "2.0",
                        "method": "get_addresses",
                        "params": [[wallet_address]]
                    }
                )

    try:
        wallet_response =   await pull_node_api(
                                api_url=app_globals.app_results[node_name]['url'],
                                api_payload=payload
                            )

        if type(wallet_response) != list or not len(wallet_response) or "address" not in wallet_response[0]:
            raise KeyError(wallet_response)

        wallet_result = wallet_response[0]
        wallet_result_address = wallet_result.get("address", "None")

        if wallet_result_address != wallet_address:
            raise TypeError(
                {
                    "error": f"Bad address received from API: '{wallet_result_address}'"
                }
            )

        wallet_final_balance = 0
        wallet_final_balance = wallet_result.get("final_balance", 0)
        wallet_final_balance = float(wallet_final_balance)
        wallet_final_balance = round(wallet_final_balance, 4)

        wallet_candidate_rolls = 0
        wallet_candidate_rolls = wallet_result.get("candidate_roll_count", 0)
        wallet_candidate_rolls = int(wallet_candidate_rolls)

        wallet_active_rolls = 0
        if type(wallet_result['cycle_infos'][-1].get("active_rolls", 0)) == int:
            wallet_active_rolls = wallet_result['cycle_infos'][-1].get("active_rolls", 0)

        wallet_missed_blocks = 0
        for cycle_info in wallet_result.get("cycle_infos", []):
            if type(cycle_info.get("nok_count", 0)) == int:
                wallet_missed_blocks += cycle_info.get("nok_count", 0)

        wallet_last_cycle_missed_blocks = 0
        if type(wallet_result['cycle_infos'][-1].get("nok_count", 0)) == int:
            wallet_last_cycle_missed_blocks = wallet_result['cycle_infos'][-1].get("nok_count", 0)

    except Exception as E:
        logger.warning(f"Error watching wallet '{wallet_address}' on '{node_name}': ({str(E)})")

        if app_globals.app_results[node_name]['wallets'][wallet_address]['last_status'] != False:
            t = as_list(
                    as_line(
                        "🏠 Node: ",
                        Code(node_name),
                        end=""
                    ),
                    as_line(f"📍 {app_globals.app_results[node_name]['url']}"),
                    as_line(
                        "🚨 Cannot get info for wallet: ",
                        TextLink(
                            get_short_address(address=wallet_address),
                            url=f"{app_globals.app_config['service']['mainnet_explorer']}/address/{wallet_address}"
                        )
                    ),
                    as_line(
                        "💻 Result: ",
                        Code(wallet_response)
                    ),
                    "⚠ Check wallet address or node settings!"
                )
            await queue_telegram_message(message_text=t.as_html())

        app_globals.app_results[node_name]['wallets'][wallet_address]['last_status'] = False
        app_globals.app_results[node_name]['wallets'][wallet_address]['last_result'] = wallet_response

    else:
        logger.info(f"Got wallet '{wallet_address}' on node '{node_name}' info successfully!")

        if app_globals.app_results[node_name]['wallets'][wallet_address]['last_status'] != True:
            t = as_list(
                    as_line(
                        "🏠 Node: ",
                        Code(node_name),
                        end=""
                    ),
                    as_line(f"📍 {app_globals.app_results[node_name]['url']}"),
                    as_line(
                        "👛 Successfully got info for wallet: ",
                        TextLink(
                            get_short_address(address=wallet_address),
                            url=f"{app_globals.app_config['service']['mainnet_explorer']}/address/{wallet_address}"
                        )
                    ),
                    f"💰 Final balance: {wallet_final_balance:,} MAS",
                    f"🧻 Candidate / Active rolls: {wallet_candidate_rolls} / {wallet_active_rolls}",
                    f"🥊 Missed blocks: {wallet_missed_blocks}"
                )
            await queue_telegram_message(message_text=t.as_html())

        else:

            # 1) Check if balance is decreased:
            if wallet_final_balance < app_globals.app_results[node_name]['wallets'][wallet_address]['final_balance']:
                t = as_list(
                        as_line(
                            "🏠 Node: ",
                            Code(node_name),
                            end=""
                        ),
                        as_line(f"📍 {app_globals.app_results[node_name]['url']}"),
                        as_line(
                            "💸 Decreased balance on wallet: ",
                            TextLink(
                                get_short_address(address=wallet_address),
                                url=f"{app_globals.app_config['service']['mainnet_explorer']}/address/{wallet_address}"
                            )
                        ),
                        f"👁 New final balance: {app_globals.app_results[node_name]['wallets'][wallet_address]['final_balance']} → {wallet_final_balance} MAS",
                    )
                await queue_telegram_message(message_text=t.as_html())

            # 2) Check if candidate rolls changed:
            if wallet_candidate_rolls != app_globals.app_results[node_name]['wallets'][wallet_address]['candidate_rolls']:
                t = as_list(
                        as_line(
                            "🏠 Node: ",
                            Code(node_name),
                            end=""
                        ),
                        as_line(f"📍 {app_globals.app_results[node_name]['url']}"),
                        as_line(
                            "🧻 Candidate rolls changed on wallet: ",
                            TextLink(
                                get_short_address(address=wallet_address),
                                url=f"{app_globals.app_config['service']['mainnet_explorer']}/address/{wallet_address}"
                            )
                        ),
                        f"👁 New candidate rolls number: {app_globals.app_results[node_name]['wallets'][wallet_address]['candidate_rolls']} → {wallet_candidate_rolls}"
                    )
                await queue_telegram_message(message_text=t.as_html())

            # 3) Check if active rolls changed:
            if wallet_active_rolls != app_globals.app_results[node_name]['wallets'][wallet_address]['active_rolls']:
                t = as_list(
                        as_line(
                            "🏠 Node: ",
                            Code(node_name),
                            end=""
                        ),
                        as_line(f"📍 {app_globals.app_results[node_name]['url']}"),
                        as_line(
                            "🧻 Active rolls changed on wallet: ",
                            TextLink(
                                get_short_address(address=wallet_address),
                                url=f"{app_globals.app_config['service']['mainnet_explorer']}/address/{wallet_address}"
                            )
                        ),
                        f"👁 New active rolls number: {app_globals.app_results[node_name]['wallets'][wallet_address]['active_rolls']} → {wallet_active_rolls}"
                    )
                await queue_telegram_message(message_text=t.as_html())

            # 4) Check if new blocks missed:
            if wallet_missed_blocks > app_globals.app_results[node_name]['wallets'][wallet_address]['missed_blocks']:
                t = as_list(
                        as_line(
                            "🏠 Node: ",
                            Code(node_name),
                            end=""
                        ),
                        as_line(f"📍 {app_globals.app_results[node_name]['url']}"),
                        as_line(
                            "🥊 New missed blocks on wallet:",
                            TextLink(
                                get_short_address(address=wallet_address),
                                url=f"{app_globals.app_config['service']['mainnet_explorer']}/address/{wallet_address}"
                            )
                        ),
                        f"👁 Blocks missed in last cycle: {wallet_last_cycle_missed_blocks}"
                    )
                await queue_telegram_message(message_text=t.as_html())

        app_globals.app_results[node_name]['wallets'][wallet_address]['last_status'] = True
        app_globals.app_results[node_name]['wallets'][wallet_address]['last_update'] = t_now()

        app_globals.app_results[node_name]['wallets'][wallet_address]['final_balance'] = wallet_final_balance
        app_globals.app_results[node_name]['wallets'][wallet_address]['candidate_rolls'] = wallet_candidate_rolls
        app_globals.app_results[node_name]['wallets'][wallet_address]['active_rolls'] = wallet_active_rolls
        app_globals.app_results[node_name]['wallets'][wallet_address]['missed_blocks'] = wallet_missed_blocks

        app_globals.app_results[node_name]['wallets'][wallet_address]['last_result'] = wallet_result

    finally:
        logger.debug(f"API result for wallet '{wallet_address}' on node '{node_name}':\n{json.dumps(obj=app_globals.app_results[node_name]['wallets'][wallet_address]['last_result'], indent=4)}")

    return




if __name__ == "__main__":
    pass
