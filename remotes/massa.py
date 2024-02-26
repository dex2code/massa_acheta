from loguru import logger

import asyncio
import json

from app_config import app_config
import app_globals

from tools import pull_http_api, t_now, save_app_stat


@logger.catch
async def massa_get_info() -> bool:
    logger.debug("-> Enter Def")

    massa_info_answer = {"error": "No response from MASSA mainnet RPC (/info)"}
    try:
        massa_info_answer = await pull_http_api(api_url=f"{app_config['service']['mainnet_rpc_url']}/info", api_method="GET")

        massa_info_result = massa_info_answer.get("result", None)
        if not massa_info_result:
            logger.warning(f"No result in MASSA mainnet RPC /info answer ({str(massa_info_answer)})")
            return False

        massa_mainnet_release = massa_info_result.get("version", None)
        if not massa_mainnet_release:
            logger.warning(f"No version in MASSA mainnet RPC /info answer ({str(massa_info_answer)})")
            return False

        massa_total_stakers = massa_info_result.get("n_stakers", None)
        if not massa_total_stakers:
            logger.warning(f"No stakers in MASSA mainnet RPC /info answer ({str(massa_info_answer)})")
            return False

        massa_current_cycle = massa_info_result.get("current_cycle", None)
        if not massa_current_cycle:
            logger.warning(f"No stakers in MASSA mainnet RPC /info answer ({str(massa_info_answer)})")
            return False

    except BaseException as E:
        logger.warning(f"Cannot operate MASSA mainnet RPC /info answer: ({str(E)})")
        return False

    else:
        app_globals.massa_network['values']['current_release'] = massa_mainnet_release
        app_globals.massa_network['values']['total_stakers'] = massa_total_stakers
        app_globals.massa_network['values']['current_cycle'] = massa_current_cycle
        return True



@logger.catch
async def massa_get_status() -> bool:
    logger.debug("-> Enter Def")

    payload = json.dumps(
        {
            "id": 0,
            "jsonrpc": "2.0",
            "method": "get_status",
            "params": []
        }
    )

    massa_status_answer = {"error": "No response from remote HTTP API"}
    try:
        massa_status_answer = await pull_http_api(api_url=app_config['service']['mainnet_rpc_url'],
                                                  api_method="POST",
                                                  api_payload=payload,
                                                  api_root_element="result")
        
        massa_status_result = massa_status_answer.get("result", None)
        if not massa_status_result:
            logger.warning(f"No result in MASSA mainnet RPC 'get_status' answer ({str(massa_status_answer)})")
            return False

        massa_status_config = massa_status_result.get("config", None)
        if not massa_status_config or type(massa_status_config) != dict:
            logger.warning(f"No config in MASSA mainnet RPC 'get_status' answer ({str(massa_status_answer)})")
            return False
        else:
            app_globals.massa_config = massa_status_config.copy()

        massa_block_reward = massa_status_config.get("block_reward", None)
        if not massa_block_reward:
            logger.warning(f"No block_reward in MASSA mainnet RPC 'get_status' answer ({str(massa_status_answer)})")
            return False
        else:
            massa_block_reward = float(massa_block_reward)

        massa_roll_price = massa_status_config.get("roll_price", None)
        if not massa_roll_price:
            logger.warning(f"No roll_price in MASSA mainnet RPC 'get_status' answer ({str(massa_status_answer)})")
            return False
        else:
            massa_roll_price = int(
                float(massa_roll_price)
            )

    except BaseException as E:
        logger.warning(f"Cannot operate MASSA mainnet RPC get_status answer: ({str(E)})")
        return False

    else:
        app_globals.massa_network['values']['block_reward'] = massa_block_reward
        app_globals.massa_network['values']['roll_price'] = massa_roll_price
        return True



@logger.catch
async def massa_get_stakers() -> bool:
    logger.debug("-> Enter Def")

    massa_total_rolls = 0
    massa_stakers_offset = 0
    massa_stakers_bundle_length = app_config['service']['mainnet_stakers_bundle']

    while massa_stakers_bundle_length == app_config['service']['mainnet_stakers_bundle']:
        logger.debug(f"massa_get_stakers loop with offset {massa_stakers_offset}")

        payload = json.dumps(
            {
                "id": 0,
                "jsonrpc": "2.0",
                "method": "get_stakers",
                "params": [
                    {
                        "offset": massa_stakers_offset,
                        "limit": app_config['service']['mainnet_stakers_bundle']
                    }
                ]
            }
        )

        massa_stakers_answer = {"error": "No response from remote HTTP API"}
        try:
            massa_stakers_answer = await pull_http_api(api_url=app_config['service']['mainnet_rpc_url'],
                                                    api_method="POST",
                                                    api_payload=payload,
                                                    api_root_element="result")

            massa_stakers_result = massa_stakers_answer.get("result", None)
            if not massa_stakers_result or type(massa_stakers_result) != list:
                logger.warning(f"No result in MASSA mainnet RPC 'get_stakers' answer ({str(massa_stakers_answer)})")
                return False

            massa_stakers_bundle_length = len(massa_stakers_result)        
            if massa_stakers_bundle_length == 0:
                logger.warning(f"Zero length of stakers list!")
            
            for staker in massa_stakers_result:
                if type(staker) != list or len(staker) != 2:
                    logger.warning(f"Cannot take rolls number from staker '{staker}'")
                    continue
                massa_total_rolls += int(staker[1])

        except BaseException as E:
            logger.warning(f"Cannot operate MASSA mainnet RPC get_stakers answer: ({str(E)})")
            return False

        else:
            massa_stakers_offset += 1

        await asyncio.sleep(delay=1)

    app_globals.massa_network['values']['total_staked_rolls'] = massa_total_rolls
    return True



@logger.catch
async def massexplo_get_data() -> bool:
    logger.debug("-> Enter Def")

    massexplo_data_answer = {"error": "No response from remote HTTP API"}
    try:
        massexplo_data_answer = await pull_http_api(api_url=app_config['service']['massexplo_api_url'],
                                                  api_method="GET",
                                                  api_root_element="data")
        
        massexplo_data_result = massexplo_data_answer.get("result", None)
        if not massexplo_data_result:
            logger.warning(f"No result in massexplo.io /info answer ({str(massexplo_data_answer)})")
            return False

        massa_mainnet_release = massexplo_data_result.get("version", None)
        if not massa_mainnet_release:
            logger.warning(f"No version in massexplo.io /info answer ({str(massexplo_data_answer)})")
            return False

        massa_total_stakers = massexplo_data_result.get("stakers", None)
        if not massa_total_stakers:
            logger.warning(f"No stakers in massexplo.io /info answer ({str(massexplo_data_answer)})")
            return False

        massa_current_cycle = massexplo_data_result.get("current_cycle", None)
        if not massa_current_cycle:
            logger.warning(f"No current_cycle in massexplo.io /info answer ({str(massexplo_data_answer)})")
            return False

        massa_block_reward = massexplo_data_result.get("block_reward", None)
        if not massa_block_reward:
            logger.warning(f"No block_reward in massexplo.io /info answer ({str(massexplo_data_answer)})")
            return False
        else:
            massa_block_reward = float(massa_block_reward)

        massa_roll_price = massexplo_data_result.get("roll_price", None)
        if not massa_roll_price:
            logger.warning(f"No roll_price in massexplo.io /info answer ({str(massexplo_data_answer)})")
            return False
        else:
            massa_roll_price = int(
                float(massa_roll_price)
            )

        massa_total_rolls = massexplo_data_result.get("stakers_total_rolls", None)
        if not massa_total_rolls:
            logger.warning(f"No stakers_total_rolls in massexplo.io /info answer ({str(massexplo_data_answer)})")
            return False
        else:
            massa_total_rolls = int(massa_total_rolls)

    except BaseException as E:
        logger.warning(f"Cannot operate massexplo.io /info answer: ({str(E)})")
        return False

    else:
        app_globals.massa_network['values']['current_release'] = massa_mainnet_release
        app_globals.massa_network['values']['total_stakers'] = massa_total_stakers
        app_globals.massa_network['values']['current_cycle'] = massa_current_cycle
        app_globals.massa_network['values']['block_reward'] = massa_block_reward
        app_globals.massa_network['values']['roll_price'] = massa_roll_price
        app_globals.massa_network['values']['total_staked_rolls'] = massa_total_rolls
        return True


@logger.catch
async def massa() -> None:
    logger.debug("-> Enter Def")

    try:
        while True:
            success_flag = True

            if success_flag and await massa_get_info():
                logger.info(f"Successfully pulled /info from MASSA mainnet RPC")
                await asyncio.sleep(delay=1)
            else:
                success_flag = False
                logger.warning(f"Error pulling /info from MASSA mainnet RPC")

            if success_flag and await massa_get_status():
                logger.info(f"Successfully pulled get_status from MASSA mainnet RPC")
                await asyncio.sleep(delay=1)
            else:
                success_flag = False
                logger.warning(f"Error pulling get_status from MASSA mainnet RPC")

            if success_flag and await massa_get_stakers():
                logger.info(f"Successfully pulled get_stakers from MASSA mainnet RPC")
                await asyncio.sleep(delay=1)
            else:
                success_flag = False
                logger.warning(f"Error pulling get_stakers from MASSA mainnet RPC")

            if not success_flag:
                if await massexplo_get_data():
                    success_flag = True
                    logger.info(f"Successfully pulled /info from massexplo.io")
                else:
                    logger.warning(f"Error pulling /info from massexplo.io")

            if success_flag:
                logger.info(f"Successfully collected MASSA mainnet network info")

                time_now = await t_now()

                try:
                    app_globals.massa_network['values']['last_updated'] = time_now
                    app_globals.massa_network['stat'].append(
                        {
                            "time": time_now,
                            "cycle": app_globals.massa_network['values']['current_cycle'],
                            "stakers": app_globals.massa_network['values']['total_stakers'],
                            "rolls": app_globals.massa_network['values']['total_staked_rolls']
                        }
                    )
                
                except BaseException as E:
                    logger.warning(f"Cannot store MASSA stat ({str(E)})")

                else:
                    logger.info(f"Successfully stored MASSA stat ({len(app_globals.massa_network['stat'])} measures)")

            else:
                logger.warning(f"Could not collect MASSA mainnet network info")

            logger.info(f"Sleeping for {app_config['service']['massa_network_update_period_min'] * 60} seconds...")
            await asyncio.sleep(delay=app_config['service']['massa_network_update_period_min'] * 60)

            save_app_stat()

    except BaseException as E:
        logger.error(f"Exception {str(E)} ({E})")
    
    finally:
        logger.error(f"<- Quit Def")

    return




if __name__ == "__main__":
    pass
