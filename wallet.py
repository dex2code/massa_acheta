from loguru import logger
from init import app_results
from tools import pull_node_api, send_telegram_message
from time import time as t_now

import json



@logger.catch
async def check_wallet(node_name: str="", wallet_addr: str="") -> None:
    logger.debug(f"-> Enter def")

    if app_results[node_name]['last_status'] != True:
        logger.warning(f"Will not watch wallet '{wallet_addr}' on node '{node_name}' because of its offline")
        return

    payload = json.dumps({
        "id": 0,
        "jsonrpc": "2.0",
        "method": "get_addresses",
        "params": [[wallet_addr]]
    })

    try:
        wallet_response = await pull_node_api(api_url=app_results[node_name]['url'], api_payload=payload)
        wallet_result = wallet_response[0]

        wallet_final_balance = round(float(wallet_result['final_balance']), 4)
        wallet_candidate_rolls = int(wallet_result['candidate_roll_count'])

        if type(wallet_result['cycle_infos'][-1]['active_rolls']) == int:
            wallet_active_rolls = int(wallet_result['cycle_infos'][-1]['active_rolls'])
        else:
            wallet_active_rolls = 0

        wallet_missed_blocks = 0
        for cycle_info in wallet_result['cycle_infos']:
            if type(cycle_info['nok_count']) == int:
                wallet_missed_blocks += int(cycle_info['nok_count'])

        wallet_last_cycle_missed_blocks = int(wallet_result['cycle_infos'][-1]['nok_count'])

    except Exception as E:
        logger.warning(f"Error watching wallet '{wallet_addr}' on '{node_name}': ({str(E)})")

        app_results[node_name]['wallets'][wallet_addr]['last_result'] = wallet_response

        if app_results[node_name]['wallets'][wallet_addr]['last_status'] != False:
            app_results[node_name]['wallets'][wallet_addr]['last_status'] = False
            await send_telegram_message(message_text=f"🙀 Node '<b>{node_name}</b>': Cannot get info for wallet:\n\n<pre>{wallet_addr}</pre>\n\n<code>💻  {wallet_response}</code>\n\n⚠ Check wallet address or node settings.")

    else:
        logger.info(f"Got wallet '{wallet_addr}' on node '{node_name}' info successfully!")

        app_results[node_name]['wallets'][wallet_addr]['last_update'] = t_now()

        if app_results[node_name]['wallets'][wallet_addr]['last_status'] != True:
            app_results[node_name]['wallets'][wallet_addr]['last_status'] = True
            await send_telegram_message(message_text=f"👛 Node '<b>{node_name}</b>': Successfully got info for wallet:\n\n<pre>{wallet_addr}</pre>\n\n<pre> • Final balance: {wallet_final_balance}\n • Candidate rolls: {wallet_candidate_rolls}\n • Active rolls: {wallet_active_rolls}\n • Missed blocks: {wallet_missed_blocks}</pre>")

        app_results[node_name]['wallets'][wallet_addr]['last_result'] = wallet_result


        # 1) Check if balance is decreased:
        if wallet_final_balance < app_results[node_name]['wallets'][wallet_addr]['final_balance']:
            await send_telegram_message(message_text=f"💸 Node '<b>{node_name}</b>': Decreased balance on wallet:\n\n<pre>{wallet_addr}</pre>\n\nNew final balance:\n\n<pre>{app_results[node_name]['wallets'][wallet_addr]['final_balance']} → {wallet_final_balance}</pre>")
        app_results[node_name]['wallets'][wallet_addr]['final_balance'] = wallet_final_balance


        # 2) Check if candidate rolls changed:
        if wallet_candidate_rolls != app_results[node_name]['wallets'][wallet_addr]['candidate_rolls']:
            await send_telegram_message(message_text=f"⚙ Node '<b>{node_name}</b>': Candidate rolls changed on wallet:\n\n<pre>{wallet_addr}</pre>\n\nNew candidate rolls number:\n\n<pre>{app_results[node_name]['wallets'][wallet_addr]['candidate_rolls']} → {wallet_candidate_rolls}</pre>")
        app_results[node_name]['wallets'][wallet_addr]['candidate_rolls'] = wallet_candidate_rolls


        # 3) Check if active rolls changed:
        if wallet_active_rolls != app_results[node_name]['wallets'][wallet_addr]['active_rolls']:
            await send_telegram_message(message_text=f"⛽ Node '<b>{node_name}</b>': Active rolls changed on wallet:\n\n<pre>{wallet_addr}</pre>\n\nNew active rolls number:\n\n<pre>{app_results[node_name]['wallets'][wallet_addr]['active_rolls']} → {wallet_active_rolls}</pre>")
        app_results[node_name]['wallets'][wallet_addr]['active_rolls'] = wallet_active_rolls


        # 4) Check if new blocks missed:
        if wallet_missed_blocks > app_results[node_name]['wallets'][wallet_addr]['missed_blocks']:
            await send_telegram_message(message_text=f"🥊 Node '<b>{node_name}</b>': New missed blocks on wallet:\n\n<pre>{wallet_addr}</pre>\n\nBlocks missed in last cycle:\n\n<pre>{wallet_last_cycle_missed_blocks}</pre>")
        app_results[node_name]['wallets'][wallet_addr]['missed_blocks'] = wallet_missed_blocks

    finally:
        logger.debug(f"API result for wallet '{wallet_addr}' on node '{node_name}':\n{json.dumps(obj=wallet_response, indent=4)}")

    return
