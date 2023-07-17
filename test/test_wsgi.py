import requests
import time
from concurrent.futures import ThreadPoolExecutor

url = 'http://127.0.0.1:12007/getBalance/'

headers = {
    'Content-Type': 'application/json',
}

data = {
    "network": "polygon-mumbai",
    "address": "0x1281F6d1b450E22FE4f119Cbc2bc8D4b713564D4",
    "quoteCurrency": "USDT",
    "currencies": ["MATIC", "USDT", "USDC"]
}

def send_request():
    start_time = time.time()
    response = requests.post(url, headers=headers, json=data)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken for request: {elapsed_time} seconds")
    return response.json()

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(send_request) for _ in range(10)]

for future in futures:
    response = future.result()
    print(response)

