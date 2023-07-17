#!/bin/bash
url='http://127.0.0.1:12007/getBalance/'
data='{
    "network": "polygon-mumbai",
    "address": "0x1281F6d1b450E22FE4f119Cbc2bc8D4b713564D4",
    "quoteCurrency": "USDT",
    "currencies": [
        "MATIC",
        "USDT",
        "USDC"
    ]
}'

# 设置循环次数
num_requests=10

# 发送请求并计算时间
for ((i=1; i<=num_requests; i++))
do
    start_time=$(date +%s%N)
    response=$(curl --location --header 'Content-Type: application/json' --data "$data" "$url")
    end_time=$(date +%s%N)
    duration=$(echo "scale=2; ($end_time - $start_time) / 1000000" | bc)

    echo "Request $i: $duration ms"
    echo "$response"
done

