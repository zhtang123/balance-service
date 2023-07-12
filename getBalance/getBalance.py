import os
from web3 import Web3
from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

with open('tokens.json', 'r') as f:
    token_data = json.load(f)

ip = os.environ['IP']

def get_token_price(token_symbol):
    response = requests.post(f'http://{ip}/price24h/', json={"tokens": [token_symbol]})
    data = response.json()['data']

    for item in data:
        if token_symbol in item:
            if item[token_symbol]['success']:
                return item[token_symbol]['price'], item[token_symbol]['priceChangePercent']
            else:
                return None, None

    return None, None

@app.route('/getBalance/', methods=['POST'])
def getBalance():
    data = request.get_json()
    chain = data['network']
    address = data['address']
    additional_tokens = data.get('currencies', [])
    failed = []

    tokens = []
    for token in additional_tokens:
        if Web3.is_address(token):  # if the token is an address
            tokens.append(token)
        else:  # if the token is a name
            if chain in token_data and token in token_data[chain]:
                tokens.append(token_data[chain][token])
            else:
                failed.append({
                    'currency': token,
                    'success': 'false'
                })

    response = requests.post('http://localhost:12006/token_balance/', json={
        'chain': chain,
        'address': address,
        'token_addresses': tokens
    })

    balances = response.json()['currencies']

    total_balance_in_usdt = 0

    for item in balances:
        token_symbol = item['currency']
        price, price_change_percent = get_token_price(token_symbol)

        item['price'] = price
        item['priceChangePercent'] = price_change_percent
        item['success'] = 'true'

        # calculate total balance in USDT
        if price is not None:
            total_balance_in_usdt += int(item['balance']) / (10 ** item['currencyDecimals']) * price

    return jsonify({
        "walletBalance": {
            "quoteCurrency": data['quoteCurrency'],
            "quoteCurrencyDecimals": 6,
            "currentBalance": str(total_balance_in_usdt)
        },
        "currencies": failed + balances
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=12007)
