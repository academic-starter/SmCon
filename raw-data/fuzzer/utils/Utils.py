from typing import Type 

from web3 import Web3
from web3.contract import Contract 
from web3._utils.abi import get_constructor_abi

w3 = Web3(Web3.HTTPProvider(f'HTTP://127.0.0.1:8545'))

def deploy(contract_abi, contract_bytecode, constructor_args, deployer, private_key):
    contract = w3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
    construct_txn = contract.constructor(**constructor_args).build_transaction({
        'chainId': 1,  
        'gas': 2000000,  
        'gasPrice': w3.to_wei('50', 'gwei'),
        'nonce': w3.eth.get_transaction_count(deployer),
    })
    signed_txn = w3.eth.account.sign_transaction(construct_txn, private_key)

    transaction_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
    contract_address = transaction_receipt['contractAddress']
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)
    return contract, transaction_receipt

def get_contract(contract_address, contract_abi) -> Type[Contract]:
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)
    return contract 

def sendTransaction(abi_func, func_args, tx_sender, private_key):
    nonce = w3.eth.get_transaction_count(tx_sender)
    gas_price = w3.eth.gas_price
    gas_limit = 2000000  # 根据合约函数复杂性调整

    transaction = abi_func(**func_args).build_transaction({
            'chainId': 1,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'nonce': nonce,
        })

    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    try:
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        transaction_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(tx_hash.hex(), "transaction success")
        return transaction_receipt
    except:
        raise Exception("transaction revert")

def get_transaction_receipt(tx_hash):
    tx_receipt = w3.eth.get_transaction_receipt(tx_hash)
    tx_receipt = dict(tx_receipt)
    tx_receipt["transactionHash"] = tx_receipt["transactionHash"].hex()
    tx_receipt["blockHash"] = tx_receipt["blockHash"].hex()
    tx_receipt["logsBloom"] = tx_receipt["logsBloom"].hex()
    return tx_receipt

def get_transaction_info(tx_hash):
    transaction_details = w3.eth.get_transaction(tx_hash)
    tx_input = transaction_details.input.hex()
    tx_gas = transaction_details.gas
    tx_gasPrice = transaction_details.gasPrice 
    tx_value = transaction_details.value 
    tx_nonce = transaction_details.nonce 
    return tx_input, tx_gas, tx_gasPrice, tx_value, tx_nonce




if __name__ == "__main__":
    tx_hash = "0x46de30bfc786d05c10457b31759d2f5629c97da33f4627342477606e6bef2364"
    get_transaction_info(tx_hash=tx_hash)