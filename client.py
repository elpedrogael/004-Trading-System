import hashlib
import hmac

import requests
import time

from urllib.parse import urlencode


class BinanceTestClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = 'https://testnet.binance.vision/api'

    def _generate_signature(self, query_string: str) -> str:
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def _execute_request(self, endpoint: str, params: dict, method: str = 'GET'):
        timestamp = int(time.time() * 1000)
        params['timestamp'] = timestamp

        query_string = urlencode(params)
        signature = self._generate_signature(query_string)
        params['signature'] = signature

        headers = {
            'X-MBX-APIKEY': self.api_key
        }

        if method == 'GET':
            response = requests.get(f"{self.base_url}{endpoint}", params=params, headers=headers)
        elif method == 'POST':
            response = requests.post(f"{self.base_url}{endpoint}", params=params, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")

        return response.json()

    def get_account_info(self):
        """Get account information"""
        endpoint = '/v3/account'
        params = {}
        return self._execute_request(endpoint, params)

    def get_symbol_price(self, symbol: str):
        """Get current price for a symbol"""
        endpoint = '/v3/ticker/price'
        params = {'symbol': symbol.upper()}
        return requests.get(f"{self.base_url}{endpoint}", params=params).json()

    def get_klines(self, symbol: str, interval: str):
        """Get historical price data (klines/candlesticks)"""
        endpoint = '/v3/klines'
        params = {
            'symbol': symbol.upper(),
            'interval': interval,
            'limit': 100  # Default limit of 100 candles
        }
        return requests.get(f"{self.base_url}{endpoint}", params=params).json()

    def create_order(self, symbol: str, side: str, order_type: str, quantity: float, test: bool = True):
        """Create a new order"""
        endpoint = '/v3/order/test' if test else '/v3/order'
        params = {
            'symbol': symbol.upper(),
            'side': side.upper(),
            'type': order_type.upper(),
            'quantity': str(quantity),
        }
        return self._execute_request(endpoint, params, method='POST')
