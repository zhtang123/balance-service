import os
from web3 import Web3
from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

with open('tokens.json', 'r') as f:
    token_data = json.load(f)

ip = os.environ['IP']


def get_token_price(token_symbols):
    response = requests.post(f'http://{ip}/price24h/', json={"tokens": token_symbols})
    data = response.json()['data']

    result = {}
    for token_symbol in token_symbols:
        for item in data:
            if token_symbol in item:
                if item[token_symbol]['success']:
                    result[token_symbol] = (item[token_symbol]['price'], item[token_symbol]['priceChangePercent'])
                else:
                    result[token_symbol] = (None, None)

    return result

@app.route('/getBalance/', methods=['POST'])
def getBalance():
    data = request.get_json()
    chain = data['network']
    address = Web3.to_checksum_address(data['address'])
    additional_tokens = data.get('currencies', [])
    failed = []
    tokens = []
    native = None
    total_price_change_percent = 0

    for token in additional_tokens:
        if Web3.is_address(token):  # if the token is an address
            tokens.append(token)
        else:  # if the token is a name
            if chain in token_data and token in token_data[chain]:
                tokens.append(token_data[chain][token])
                if token_data[chain][token] == 'native':
                    native = token
            else:
                failed.append({
                    'currency': token,
                    'success': 'false'
                })

    response = requests.post(f'http://{os.environ["TOKEN_BALANCE"]}:12006/token_balance/', json={
        'chain': chain,
        'address': address,
        'token_addresses': tokens
    })

    balances = response.json()['currencies']
    for item in balances:
        if item['currency'] == 'native':
            item['currency'] = native

    total_balance_in_usdt = 0

    prices = get_token_price([item['currency'] for item in balances])

    for item in balances:
        token_symbol = item['currency']
        price, price_change_percent = prices[token_symbol]

        item['price'] = price
        item['priceChangePercent'] = price_change_percent
        item['success'] = 'true'

        # calculate total balance in USDT
        if price is not None:
            item['currentBalanceInQuoteCurrency'] = int(int(item['balance']) / (10 ** item['currencyDecimals']) * (10 ** 6) * price)
            total_balance_in_usdt += item['currentBalanceInQuoteCurrency']

            # calculate weighted price change percent
            if price_change_percent is not None:
                total_price_change_percent += price_change_percent * item['currentBalanceInQuoteCurrency']
        else:
            item['currentBalanceInQuoteCurrency'] = 0

    # calculate average price change percent
    average_price_change_percent = total_price_change_percent / total_balance_in_usdt if total_balance_in_usdt != 0 else None

    # calculate actual value change
    actual_value_change = total_balance_in_usdt * (average_price_change_percent / 100) if average_price_change_percent is not None else None

    return jsonify({
        "walletBalance": {
            "quoteCurrency": data['quoteCurrency'],
            "quoteCurrencyDecimals": 6,
            "currentBalance": int(total_balance_in_usdt),
            "averagePriceChangePercent": average_price_change_percent,
            "actualValueChange": actual_value_change
        },
        "currencies": failed + balances
    })


if __name__ == '__main__':
    pass
