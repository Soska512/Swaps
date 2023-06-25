from loguru import logger
from web3 import Web3, Account
import time, json
from web3.auto import w3
from sys import stderr
import random

bsc_rpc_url = 'https://1rpc.io/bnb'

bsc_w3 = Web3(Web3.HTTPProvider(bsc_rpc_url))

socket_refuel_address = w3.to_checksum_address('0xBE51D38547992293c89CC589105784ab60b004A9')
socket_refuel_abi = json.load(open('./abis/socket_refuel_abi.json'))

socket_refuel_contract = bsc_w3.eth.contract(socket_refuel_address, abi=socket_refuel_abi)

def refuel_gnosis_from_bsc(account):
    address = w3.to_checksum_address(account.address)
    nonce = bsc_w3.eth.get_transaction_count(address)
    gas_price = bsc_w3.eth.gas_price
    value = random.uniform(0.002, 0.003)
    valuev = Web3.to_wei(value, 'ether')
    swap_txn = socket_refuel_contract.functions.depositNativeToken(100,
                                                    address,                              
    ).build_transaction({
        'from': address,
        'value': valuev,
        'gas': 200000,
        'gasPrice': gas_price,
        'nonce': nonce,
    })
    signed_swap_txn = bsc_w3.eth.account.sign_transaction(swap_txn, account.key)
    swap_txn_hash = bsc_w3.eth.send_raw_transaction(signed_swap_txn.rawTransaction)
    return swap_txn_hash

def main():
    logger.info("TG channel: https://t.me/cryptomicrob")
    logger.add("./logs/refuel_ {time} .log")
    with open('keys.txt', 'r') as keys_file:
        accounts = [Account.from_key(line.replace("\n", "")) for line in keys_file.readlines()]
    for account in accounts:
        logger.info(f'Started work with account: {account.address}')
        try:
            txn = refuel_gnosis_from_bsc(account)
            logger.success(f"Txn Hash: https://bscscan.com/tx/{txn.hex()}")
        except:
            logger.exception("Error")
        logger.success(f"Ended work with account: {account.address}\n"
                       "Sleeping for 20 sec")
        time.sleep(20)

main()