from loguru import logger
from web3 import Web3, Account
import time, json
from web3.auto import w3
from sys import stderr
import random

logger.remove()

logger.add(stderr, format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <cyan>{line}</cyan> - <level>{message}</level>")
celo_rpc_url = 'https://1rpc.io/celo'
gnosis_rpc_url = 'https://rpc.ankr.com/gnosis'

celo_w3 = Web3(Web3.HTTPProvider(celo_rpc_url))
gnosis_w3 = Web3(Web3.HTTPProvider(gnosis_rpc_url))

agEur_gnosis_address = w3.to_checksum_address('0x4b1E2c2762667331Bc91648052F646d1b0d35984')
agEur_Celo_address = w3.to_checksum_address('0xC16B81Af351BA9e64C1a069E3Ab18c244A1E3049')
angle_approve_gnosis_address = w3.to_checksum_address('0x4b1E2c2762667331Bc91648052F646d1b0d35984')
angle_approve_celo_address = w3.to_checksum_address('0xC16B81Af351BA9e64C1a069E3Ab18c244A1E3049')
angle_bridge_gnosis_address = '0xFA5Ed56A203466CbBC2430a43c66b9D8723528E7'
angle_bridge_celo_address = '0xf1dDcACA7D17f8030Ab2eb54f2D9811365EFe123'

agEur_Celo_abi = json.load(open('./abis/agEur_celo_abi.json'))
agEur_gnosis_abi = json.load(open('./abis/agEur_gnosis_abi.json'))
angle_approve_celo_abi = json.load(open('./abis/angle_approve_celo_abi.json'))
angle_bridge_celo_abi = json.load(open('./abis/angle_bridge_celo_abi.json'))
angle_approve_gnosis_abi = json.load(open('./abis/angle_approve_gnosis_abi.json'))
angle_bridge_gnosis_abi = json.load(open('./abis/angle_bridge_gnosis_abi.json'))

angle_bridge_gnosis_contract = gnosis_w3.eth.contract(angle_bridge_gnosis_address, abi=angle_bridge_gnosis_abi)
angle_bridge_celo_contract = celo_w3.eth.contract(angle_bridge_celo_address, abi=angle_bridge_celo_abi)
angle_approve_gnosis_contract = gnosis_w3.eth.contract(angle_approve_gnosis_address, abi=angle_approve_gnosis_abi)
angle_approve_celo_contract = celo_w3.eth.contract(angle_approve_celo_address, abi=angle_approve_celo_abi)
agEur_gnosis_contract = gnosis_w3.eth.contract(agEur_gnosis_address, abi=agEur_gnosis_abi)
agEur_celo_contract = celo_w3.eth.contract(agEur_Celo_address, abi=agEur_Celo_abi)

def get_balance_LZ_celo(address):
    return angle_bridge_celo_contract.functions.balanceOf(address).call()

def get_balance_LZ_gnosis(address):
    return angle_bridge_gnosis_contract.functions.balanceOf(address).call()

def get_balance_agEur_gnosis(address):
    return agEur_gnosis_contract.functions.balanceOf(address).call()

def get_balance_agEur_celo(address):
    return agEur_celo_contract.functions.balanceOf(address).call()

def approve_agEur_gnosis(account):
    address = w3.to_checksum_address(account.address)
    nonce = gnosis_w3.eth.get_transaction_count(address)
    gas_price = gnosis_w3.eth.gas_price
    amount = get_balance_agEur_gnosis(address)
    swap_txn = angle_approve_gnosis_contract.functions.approve('0xFA5Ed56A203466CbBC2430a43c66b9D8723528E7',
                                                       amount                                 
    ).build_transaction({
        'from': address,
        'value': 0,
        'nonce': nonce,
    })
    swap_txn.update({'maxFeePerGas': gnosis_w3.eth.fee_history(gnosis_w3.eth.get_block_number(), 'latest')['baseFeePerGas'][-1] + gnosis_w3.eth.max_priority_fee})
    swap_txn.update({'maxPriorityFeePerGas': gnosis_w3.eth.max_priority_fee})

    gasLimit = gnosis_w3.eth.estimate_gas(swap_txn)
    swap_txn.update({'gas': gasLimit})

    signed_swap_txn = gnosis_w3.eth.account.sign_transaction(swap_txn, account.key)
    swap_txn_hash = gnosis_w3.eth.send_raw_transaction(signed_swap_txn.rawTransaction)
    return swap_txn_hash

def swap_agEur_gnosis_to_celo(account):
    address = w3.to_checksum_address(account.address)
    nonce = gnosis_w3.eth.get_transaction_count(address)
    gas_price = gnosis_w3.eth.gas_price
    amount = get_balance_agEur_gnosis(address)
    if amount != 0:
        fees = angle_bridge_gnosis_contract.functions.estimateSendFee(125,
                                                           address,
                                                           amount,
                                                           True,
                                                           '0x00010000000000000000000000000000000000000000000000000000000000030d40'
                                                                         ).call()
        fee = fees[0]

        swap_txn = angle_bridge_gnosis_contract.functions.send(125,
                                                    address,
                                                    amount,
                                                    address,
                                                    '0x0000000000000000000000000000000000000000',
                                                    '0x00010000000000000000000000000000000000000000000000000000000000030d40'                              
        ).build_transaction({
        'from': address,
        'value': fee,
        'nonce': nonce,
        })
        swap_txn.update({'maxFeePerGas': gnosis_w3.eth.fee_history(gnosis_w3.eth.get_block_number(), 'latest')['baseFeePerGas'][-1] + gnosis_w3.eth.max_priority_fee})
        swap_txn.update({'maxPriorityFeePerGas': gnosis_w3.eth.max_priority_fee})

        gasLimit = gnosis_w3.eth.estimate_gas(swap_txn)
        swap_txn.update({'gas': gasLimit})

        signed_swap_txn = gnosis_w3.eth.account.sign_transaction(swap_txn, account.key)
        swap_txn_hash = gnosis_w3.eth.send_raw_transaction(signed_swap_txn.rawTransaction)
        return swap_txn_hash
    elif amount == 0:
        swap_txn = angle_bridge_gnosis_contract.functions.withdraw(get_balance_LZ_gnosis(address),
                                                    address,
        ).build_transaction({
        'from': address,
        'value': 0,
        'nonce': nonce,
        })
        swap_txn.update({'maxFeePerGas': gnosis_w3.eth.fee_history(gnosis_w3.eth.get_block_number(), 'latest')['baseFeePerGas'][-1] + gnosis_w3.eth.max_priority_fee})
        swap_txn.update({'maxPriorityFeePerGas': gnosis_w3.eth.max_priority_fee})

        gasLimit = gnosis_w3.eth.estimate_gas(swap_txn)
        swap_txn.update({'gas': gasLimit})        
        signed_swap_txn = gnosis_w3.eth.account.sign_transaction(swap_txn, account.key)
        swap_txn_hash = gnosis_w3.eth.send_raw_transaction(signed_swap_txn.rawTransaction)
        time.sleep(30)

        fees = angle_bridge_gnosis_contract.functions.estimateSendFee(125,
                                                           address,
                                                           amount,
                                                           True,
                                                           '0x00010000000000000000000000000000000000000000000000000000000000030d40'
                                                                         ).call()
        fee = fees[0]

        swap_txn = angle_bridge_gnosis_contract.functions.send(125,
                                                    address,
                                                    amount,
                                                    address,
                                                    '0x0000000000000000000000000000000000000000',
                                                    '0x00010000000000000000000000000000000000000000000000000000000000030d40'                              
        ).build_transaction({
        'from': address,
        'value': fee,
        'nonce': nonce,
        })
        swap_txn.update({'maxFeePerGas': gnosis_w3.eth.fee_history(gnosis_w3.eth.get_block_number(), 'latest')['baseFeePerGas'][-1] + gnosis_w3.eth.max_priority_fee})
        swap_txn.update({'maxPriorityFeePerGas': gnosis_w3.eth.max_priority_fee})

        gasLimit = gnosis_w3.eth.estimate_gas(swap_txn)
        swap_txn.update({'gas': gasLimit})

        signed_swap_txn = gnosis_w3.eth.account.sign_transaction(swap_txn, account.key)
        swap_txn_hash = gnosis_w3.eth.send_raw_transaction(signed_swap_txn.rawTransaction)
        return swap_txn_hash

def approve_agEur_celo(account):
    address = w3.to_checksum_address(account.address)
    nonce = celo_w3.eth.get_transaction_count(address)
    gas_price = celo_w3.eth.gas_price
    amount = get_balance_agEur_celo(address)
    swap_txn = angle_approve_celo_contract.functions.approve('0xf1dDcACA7D17f8030Ab2eb54f2D9811365EFe123',
                                                       amount                               
    ).build_transaction({
        'from': address,
        'value': 0,
        'gas': 100000,
        'gasPrice': gas_price,
        'nonce': nonce,
    })
    signed_swap_txn = celo_w3.eth.account.sign_transaction(swap_txn, account.key)
    swap_txn_hash = celo_w3.eth.send_raw_transaction(signed_swap_txn.rawTransaction)
    return swap_txn_hash

def swap_agEur_celo_to_gnosis(account):
    address = w3.to_checksum_address(account.address)
    nonce = celo_w3.eth.get_transaction_count(address)
    gas_price = celo_w3.eth.gas_price
    amount = get_balance_agEur_celo(address)
    if amount != 0:
        fees = angle_bridge_celo_contract.functions.estimateSendFee(145,
                                                           address,
                                                           amount,
                                                           True,
                                                           '0x00010000000000000000000000000000000000000000000000000000000000030d40'
                                                                         ).call()
        fee = fees[0]

        swap_txn = angle_bridge_celo_contract.functions.send(145,
                                                    address,
                                                    amount,
                                                    address,
                                                    '0x0000000000000000000000000000000000000000',
                                                    '0x00010000000000000000000000000000000000000000000000000000000000030d40'                              
        ).build_transaction({
        'from': address,
        'value': fee,
        'gas': 300000,
        'gasPrice': gas_price,
        'nonce': nonce,
        })
        signed_swap_txn = celo_w3.eth.account.sign_transaction(swap_txn, account.key)
        swap_txn_hash = celo_w3.eth.send_raw_transaction(signed_swap_txn.rawTransaction)
        return swap_txn_hash
    else:
        swap_txn = angle_bridge_celo_contract.functions.withdraw(get_balance_LZ_celo(address),
                                                    address                             
        ).build_transaction({
        'from': address,
        'value': 0,
        'gas': 400000,
        'gasPrice': gas_price,
        'nonce': nonce,
        })
        signed_swap_txn = celo_w3.eth.account.sign_transaction(swap_txn, account.key)
        swap_txn_hash = celo_w3.eth.send_raw_transaction(signed_swap_txn.rawTransaction)
        time.sleep(30)

        fees = angle_bridge_celo_contract.functions.estimateSendFee(145,
                                                           address,
                                                           amount,
                                                           True,
                                                           '0x00010000000000000000000000000000000000000000000000000000000000030d40'
                                                                         ).call()
        fee = fees[0]

        swap_txn = angle_bridge_celo_contract.functions.send(145,
                                                    address,
                                                    amount,
                                                    address,
                                                    '0x0000000000000000000000000000000000000000',
                                                    '0x00010000000000000000000000000000000000000000000000000000000000030d40'                              
        ).build_transaction({
        'from': address,
        'value': fee,
        'gas': 300000,
        'gasPrice': gas_price,
        'nonce': nonce,
        })
        signed_swap_txn = celo_w3.eth.account.sign_transaction(swap_txn, account.key)
        swap_txn_hash = celo_w3.eth.send_raw_transaction(signed_swap_txn.rawTransaction)
        return swap_txn_hash


def main():
    logger.info("TG channel: https://t.me/cryptomicrob")
    logger.add("./logs/swaps_ {time} .log")
    with open('keys.txt', 'r') as keys_file:
        accounts = [Account.from_key(line.replace("\n", "")) for line in keys_file.readlines()]
    rounds:int = int(input("Количество прокрутов туда-обратно: \n"))
    for account in accounts:
        now_round = 0
        logger.info(f'Started work with account: {account.address}')
        while now_round < rounds:
            print("Gnosis -> CELO")
            try:
                get_balance_agEur_gnosis(account.address)
                approve_agEur_gnosis(account)
                time.sleep(random.randint(10, 20))
                txn = swap_agEur_gnosis_to_celo(account)
                logger.success(f"Tx hash: https://gnosisscan.io/tx/{txn.hex()}")
                time.sleep(random.randint(60, 80))
            except:
                logger.exception("Error")
            print("Celo -> Gnosis")
            try:
                get_balance_agEur_celo(account.address)
                approve_agEur_celo(account)
                time.sleep(random.randint(10, 20))
                txn = swap_agEur_celo_to_gnosis(account)
                logger.success(f"Tx hash: https://celoscan.io/tx/{txn.hex()}")
            except:
                logger.exception("Error")
            now_round += 1
            continue
        logger.success(f"Ended work with account: {account.address}\n"
                       "Sleeping for 20 sec")
        time.sleep(random.randint(10, 20))

main()