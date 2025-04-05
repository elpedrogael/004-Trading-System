from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os

from dotenv import load_dotenv

from models import PriceInfo, CandleInfo
from client import BinanceTestClient
from models import AccountInfo, OrderRequest

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",  # Add your frontend URL here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
client = BinanceTestClient(api_key, api_secret)


@app.get("/api/health")
async def health():
    return {"message": "OK"}


@app.get("/api/account")
async def get_account() -> AccountInfo:
    """
    Get Binance account information
    """
    try:
        info = client.get_account_info()
        print(f"Account Info Response: {info}")  # Debug: Log raw response
        if 'balances' not in info:
            raise ValueError(f"Unexpected response from Binance: {info}")
        balances = {bal['asset']: bal for bal in info ['balances']}

        def get_balance(asset: str):
            if asset in balances:
                return{'asset': asset, 'balance': balances[asset].get('free', '0')}
            return None

        return AccountInfo(
            uid = info.get('accountNumber', 0),
            account_type = info.get('accountType', 'SPOT'),
            btc_balance = get_balance('BTC'),
            usdt_balance = get_balance('USDT'),
            eth_balance = get_balance('ETH')
        )
    except Exception as e:
        print(f'Error al obtener cuenta: {e}')
        raise HTTPException(status_code = 500, detail = str(e))

@app.get("/api/price")
async def get_price(symbol: str) -> PriceInfo:
    """
    Get price of a symbol
    """
    try:
        price_data = client.get_symbol_price(symbol)
        return PriceInfo(
            symbol=symbol.upper(),
            price=price_data['price']
        )
    except Exception as e:
        print(f'Error al obtener precio: {e}')
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/price-history")
async def get_price(symbol: str, interval: str = '1h') -> List[CandleInfo]:
    """
    Get price of a symbol
    """
    try:
        history = client.get_klines(symbol, interval)
        return [CandleInfo(
            open_time=str(candle[0]),
            open=float(candle[1]),
            high=float(candle[2]),
            low=float(candle[3]),
            close=float(candle[4]),
            volume=float(candle[5]),
            close_time=str(candle[6]),
            quote_asset_volume=float(candle[7]),
            number_of_trades=candle[8],
            taker_buy_base_asset_volume=float(candle[9]),
            taker_buy_quote_asset_volume=float(candle[10]),
            ignore=str(candle[11])
        ) for candle in history]
    except Exception as e:
        print(f'Error al obtener historial de precios: {e}')
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/order")
async def create_order(order: OrderRequest):
    """
    Create a Binance order
    """
    try:
        order_response = client.create_order(
            symbol=order.symbol,
            side=order.side,
            order_type=order.order_type,
            quantity=order.quantity,
            test=order.test
        )
        return order_response
    except Exception as e:
        print(f'Error al crear orden: {e}')
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ping")
async def ping():
    return {"status": "API is running"}
