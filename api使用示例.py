import requests

# 1. 请将 'YOUR_API_KEY' 替换为您的真实API密钥
API_KEY = "YOUR_API_KEY"
BASE_URL = "https://grassnoodle.cloud"
headers = {
    "x-key": API_KEY
}

try:
    # 查询用量
    resp = requests.get(f"{BASE_URL}/usage/me", headers=headers)
    resp.raise_for_status()
    print("API Usage:", resp.json())

    # 示例1: BTC收盘价
    resp = requests.get(f"{BASE_URL}/v1/metrics/market/price_usd_close", headers=headers, params={'a': 'BTC'})
    resp.raise_for_status()
    print("\nBTC Price (last 3):", resp.json()[-3:])

    # 示例2: ETH活跃地址
    resp = requests.get(f"{BASE_URL}/v1/metrics/addresses/active_count", headers=headers, params={'a': 'ETH'})
    resp.raise_for_status()
    print("\nETH Active Addresses (last 3):", resp.json()[-3:])

    # 示例3: BTC 2022年1月OHLC
    params_ohlc = {'a': 'BTC', 's': '1641013200', 'u': '1643605200'}
    resp = requests.get(f"{BASE_URL}/v1/metrics/market/price_usd_ohlc", headers=headers, params=params_ohlc)
    resp.raise_for_status()
    print("\nBTC Jan 2022 OHLC:", resp.json())

    # 示例4: BTC MVRV Z-Score
    resp = requests.get(f"{BASE_URL}/v1/metrics/market/mvrv_z_score", headers=headers, params={'a': 'BTC'})
    resp.raise_for_status()
    print("\nBTC MVRV Z-Score (last 3):", resp.json()[-3:])

    # 示例5: BTC: Altcoin Cycle Signal
    # 绝大部分T2,T3数据都可以使用。若显示，Please reach out to our sales team to gain access to this metric，则无法调用api。
    # 无法使用的api返回值为：{"type":"metric","requiredPlan":"professional_ml"}
    params = {
    'a': 'BTC',
    's': '1641013200',
    'u': '1643605200'
    }

    resp = requests.get(f"{BASE_URL}/v1/metrics/signals/altcoin_index", headers=headers, params=params)
    print("\nBTC Altcoin Cycle Signal:", resp.json())

except requests.exceptions.RequestException as e:
    print(f"\n请求出错: {e}")