import logging
import time
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request
from web3 import Web3
import configparser

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('config.ini')

executor = ThreadPoolExecutor(max_workers=50)


abi = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
]


def get_native_balance(web3, address):
    balance = web3.eth.get_balance(address)
    return {
        "currency": "native",  # Or any identifier you want
        "currencyDecimals": 18,  # This may vary by blockchain
        "balance": str(balance),
        "quoteCurrency": "USDT"
    }

def get_token_data(web3, token_address, address, chain):


    token_contract = web3.eth.contract(address=token_address, abi=abi)

    with ThreadPoolExecutor(max_workers=30) as executor:
        decimals_future = executor.submit(token_contract.functions.decimals().call)
        balance_future = executor.submit(token_contract.functions.balanceOf(address).call)
        symbol_future = executor.submit(token_contract.functions.symbol().call)

        decimals = decimals_future.result()
        balance = balance_future.result()
        token_symbol = symbol_future.result()


    return {
        "currency": token_symbol,
        "currencyDecimals": decimals,
        "balance": str(balance),
        "quoteCurrency": "USDT"
    }



@app.route('/token_balance/', methods=['POST'])
def token_balance():
    data = request.get_json()
    chain = data['chain']
    address = data['address']
    token_addresses = data['token_addresses']

    rpc_url = config.get('Chains', chain)
    web3 = Web3(Web3.HTTPProvider(rpc_url))

    futures = []

    for token_address in token_addresses:
        if token_address == "native":
            futures.append(executor.submit(get_native_balance, web3, address))
        else:
            futures.append(executor.submit(get_token_data, web3, token_address, address, chain))

    currencies = [future.result() for future in futures]

    return {"currencies": currencies}


if __name__ == '__main__':
    pass
