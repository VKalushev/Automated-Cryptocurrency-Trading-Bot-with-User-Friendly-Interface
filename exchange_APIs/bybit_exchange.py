from pybit.unified_trading import WebSocket
from PyQt5.QtCore import pyqtSignal, QObject
from datetime import datetime, timezone
import json
import aiohttp
import asyncio
import time
import hmac
import hashlib
import uuid

class PrivateClientWrapper(QObject):
    message_received_wallet = pyqtSignal(object)
    message_received_position = pyqtSignal(object)

    def __init__(self, api_key, secret_key,parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.secret_key = secret_key  

    def update_wallet_data(self,data):
        # print(data)
        self.message_received_wallet.emit(data)

    def subscribe_to_wallet(self):
        self.ws_private_wallet = WebSocket(
                testnet=False,
                channel_type="private",
                api_key= self.api_key,
                api_secret= self.secret_key,   
        )
        self.ws_private_wallet.wallet_stream(callback=self.update_wallet_data)
    
    def unsubscribe_from_wallet(self):
        self.ws_private_wallet.exit()


class PublicClientWrapper(QObject):
    emitter_kline_data = pyqtSignal(object)
    emitter_ticker_data = pyqtSignal(object)

    def __init__(self,parent=None):
        super().__init__(parent)
        # self.ws_public_kline = WebSocket(testnet=False,channel_type="linear")
        # self.ws_public_ticker = WebSocket(testnet=False,channel_type="linear")

    def update_kline_data(self,data):
        # print(data)
        self.emitter_kline_data.emit(data)

    def update_ticker_data(self,data):
        # print(data)
        self.emitter_ticker_data.emit(data)

    def subscribe_to_kline(self,symbol,interval):
        self.ws_public_kline = WebSocket(testnet=False,channel_type="linear")
        self.ws_public_kline.kline_stream(callback=self.update_kline_data,symbol=symbol,interval=interval)

    def subscribe_to_ticker_stream(self,symbol):
        self.ws_public_ticker = WebSocket(testnet=False,channel_type="linear")
        self.ws_public_ticker.ticker_stream(callback=self.update_ticker_data,symbol=symbol)

    def unsubscribe_from_kline(self):
        self.ws_public_kline.exit()

    def unsubscribe_from_ticker_stream(self):
        self.ws_public_ticker.exit()

class BybitExchange(QObject):
# class BybitExchange():

    url = 'https://api.bybit.com'
    recv_window = str(5000)
    emitter_wallet_data = pyqtSignal(object)
    emitter_position_data = pyqtSignal(object)
    emitter_order_history_data = pyqtSignal(object)
    emitter_trade_history_data = pyqtSignal(object)
    emitter_open_orders_data = pyqtSignal(object)
    emitter_wallet_balance_data = pyqtSignal(object)
    emitter_pnl_closed_data = pyqtSignal(object)
    emitter_get_wallet_by_coin_data = pyqtSignal(object)
    emitter_kline_data = pyqtSignal(object)
    emitter_ticker_data = pyqtSignal(object)

    def __init__(self,API_KEY = "",SECRET_KEY = ""):
        super().__init__()
        self.API_KEY = API_KEY
        self.SECRET_KEY = SECRET_KEY
        self.client = PublicClientWrapper()
        self.client.moveToThread(self.thread())
        self.client.emitter_kline_data.connect(self.handle_kline_data)
        self.client.emitter_ticker_data.connect(self.handle_ticker_data)
    
    def subscrbe_to_kline(self,symbol,interval):
        self.client.subscribe_to_kline(symbol,interval)

    def unsubscribe_from_kline(self):
        self.client.unsubscribe_from_kline()

    def handle_kline_data(self,data):
        # print(data)
        self.emitter_kline_data.emit(data)

    def subscribe_to_ticker(self,symbol):
        self.client.subscribe_to_ticker_stream(symbol)

    def subscribe_to_wallet(self):
        self.private_client = PrivateClientWrapper(self.API_KEY,self.SECRET_KEY)
        self.private_client.moveToThread(self.thread())
        self.private_client.subscribe_to_wallet()
        self.private_client.message_received_wallet.connect(self.update_wallet_data)

    def unsubscribe_from_ticker(self):
        self.client.unsubscribe_from_ticker_stream()

    def handle_ticker_data(self,data):
        self.emitter_ticker_data.emit(data)

    def set_keys(self,new_API_KEY,new_SECRET_KEY):
        self.API_KEY = new_API_KEY
        self.SECRET_KEY = new_SECRET_KEY      

    def update_wallet_data(self,data):
        self.emitter_wallet_data.emit(data)
    
    def update_position_data(self,data):
        self.emitter_position_data.emit(data)

    async def HTTP_Request(self,endPoint, method, payload, Info):
        global time_stamp
        time_stamp = str(int(time.time() * 10 ** 3))
        # time_stamp = self.gen_timestamp()
        signature = self.genSignature(payload)
        headers = {
            'X-BAPI-API-KEY': self.API_KEY,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': time_stamp,
            'X-BAPI-RECV-WINDOW': self.recv_window,
            'Content-Type': 'application/json'
        }
    
        start_time = time.time()

        async with aiohttp.ClientSession() as session:
            if method == "POST":
                async with session.post(self.url + endPoint, headers=headers, data=payload) as response:
                    response_text = await response.text()
            else:
                async with session.get(self.url + endPoint + "?" + payload, headers=headers) as response:
                    response_text = await response.text()

        elapsed_time = time.time() - start_time

        # print(response_text)
        # print(Info + " Elapsed Time : " + str(elapsed_time))

        return(response_text)

    def genSignature(self,payload):
        param_str = time_stamp + self.API_KEY + self.recv_window + payload
        hash = hmac.new(bytes(self.SECRET_KEY, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
        signature = hash.hexdigest()
        return signature
    
    def gen_timestamp(self):
        now = datetime.now(timezone.utc)
        timestamp = int(now.timestamp() * 1000)
        return str(timestamp)
    
    async def create_order(self,symbol,type,entry_type,quantity,positionIdx,take_profit=None,stop_loss=None, stop_order_type=None):
        endpoint = "/v5/order/create"
        method = "POST"
        orderLinkId = uuid.uuid4().hex
        params = {}
        if take_profit == None or stop_loss == None:
            params = f'{{"category":"linear","symbol": "{symbol}","isLeverage": "{1}","side": "{type}","positionIdx": "{positionIdx}","orderType": "{entry_type}","qty": "{quantity}","timeInForce": "GTC","orderLinkId": "' + orderLinkId + '"}}'
        else:
            params = f'{{"category":"linear","symbol": "{symbol}","isLeverage": "{1}","side": "{type}","positionIdx": "{positionIdx}","orderType": "{entry_type}","qty": "{quantity}","timeInForce": "GTC","takeProfit": "{take_profit}","tpslMode": "Full","stopLoss": "{stop_loss}","tpOrderType": "{stop_order_type}","slOrderType": "{stop_order_type}","orderLinkId": "' + orderLinkId + '"}}'

        result = await self.HTTP_Request(endpoint, method, params, "Create")
        return json.loads(result)

    async def close_trade(self,symbol,type,order_type,quantity,position_index):
        endpoint = "/v5/order/create"
        method = "POST"
        orderLinkId = uuid.uuid4().hex
        params = f'{{"category":"linear","symbol": "{symbol}","isLeverage": "{1}","side": "{type}","positionIdx": "{position_index}","orderType": "{order_type}","qty": "{quantity}","timeInForce": "GTC","orderLinkId": "' + orderLinkId + '"}}'
        result = await self.HTTP_Request(endpoint, method, params, "Close")
        return json.loads(result)

    async def switch_mode(self,symbol,mode):
        endpoint = "/v5/position/switch-mode"
        method = "POST"
        orderLinkId = uuid.uuid4().hex
        params = f'{{"category":"linear","symbol": "{symbol}","mode": "{mode}","timeInForce": "GTC","orderLinkId": "' + orderLinkId + '"}}'
        result = await self.HTTP_Request(endpoint, method, params, "Switch Mode")
        return json.loads(result)
    
    async def set_leverage(self,symbol,buyLeverage,sellLeverage):
        endpoint = "/v5/position/set-leverage"
        method = "POST"
        orderLinkId = uuid.uuid4().hex
        params = f'{{"category":"linear","symbol": "{symbol}","buyLeverage": "{buyLeverage}","sellLeverage": "{sellLeverage}","timeInForce": "GTC","orderLinkId": "' + orderLinkId + '"}}'
        result = await self.HTTP_Request(endpoint, method, params, "Set Leverage")
        return json.loads(result)

    async def instrument_info(self,category='linear',symbol="BTCUSDT"):
        endpoint = "/v5/market/instruments-info"
        method = "GET"
        query_string =f"category={category}&symbol={symbol}"
        data = await self.HTTP_Request(endpoint, method, query_string, "Get Instrument Info")
        return json.loads(data)

    async def get_wallet_by_coin(self,account_type='UNIFIED',coin='USDT'):
        endpoint = "/v5/account/wallet-balance"
        method = "GET"
        query_string =f"accountType={account_type}&coin={coin}"
        data = await self.HTTP_Request(endpoint, method, query_string, "View Wallet")

        if(len(data) > 0):
            return json.loads(data)
        
        return data

    
    async def get_order_history(self,category='linear',symbol="BTCUSDT"):
        # Create Order
        endpoint = "/v5/order/history"
        method = "GET"
        query_string =f"category={category}&symbol={symbol}"
        data = await self.HTTP_Request(endpoint, method, query_string, "Get Order History")

        self.emitter_order_history_data.emit(json.loads(data))
        

    async def get_trade_history(self,category='linear',symbol="BTCUSDT"):
        # Create Order
        endpoint = "/v5/execution/list"
        method = "GET"
        query_string =f"category={category}&symbol={symbol}"
        data = await self.HTTP_Request(endpoint, method, query_string, "Get Trade History")

        self.emitter_trade_history_data.emit(json.loads(data))

    async def get_open_orders(self,category='linear',symbol="BTCUSDT"):
        # Create Order
        endpoint = "/v5/order/realtime"
        method = "GET"
        query_string =f"category={category}&symbol={symbol}"
        data = await self.HTTP_Request(endpoint, method, query_string, "Get Open Order")

        self.emitter_open_orders_data.emit(json.loads(data))

    async def get_wallet_balance(self,account_type='UNIFIED',coin="USDT"):
        # Create Order
        endpoint = "/v5/account/wallet-balance"
        method = "GET"
        query_string =f"accountType={account_type}&symbol={coin}"
        data = await self.HTTP_Request(endpoint, method, query_string, "Get Wallet Balance")
        self.emitter_wallet_balance_data.emit(json.loads(data))
        return json.loads(data)

        
    async def get_pnl_closed(self,category='linear',symbol="BTCUSDT"):
        # Create Order
        endpoint = "/v5/position/closed-pnl"
        method = "GET"
        query_string =f"category={category}&symbol={symbol}"
        data = await self.HTTP_Request(endpoint, method, query_string, "Get Wallet Balance")
        # print(data)
        self.emitter_pnl_closed_data.emit(json.loads(data))

    
    async def get_position_info(self,category='linear',symbol="BTCUSDT"):
        # Create Order
        endpoint = "/v5/position/list"
        method = "GET"
        query_string =f"category={category}&symbol={symbol}"
        data = await self.HTTP_Request(endpoint, method, query_string, "Get Wallet Balance")
        # print(data)
        return json.loads(data)

    async def get_positions(self,category='linear',settleCoin="USDT"):
        # Create Order
        endpoint = "/v5/position/list"
        method = "GET"
        query_string =f"category={category}&settleCoin={settleCoin}"
        data = await self.HTTP_Request(endpoint, method, query_string, "Get Wallet Balance")
        # print(data)
        self.emitter_position_data.emit(json.loads(data))



# import asyncio
# from time import sleep
# by = BybitExchange('ZNxRJIueDe1e2oIfu2','syhI92xuaDhnhaLHTGWgpLSJGRMEGax4ZbfB')

# async def print_results():
#     result = await by.get_wallet_by_coin()
#     return result


# async def change_api_keys():
#                 result = await print_results()
#                 return result

# async def close_trade():
#     # await by.create_order("APEUSDT","Sell","Market", 1, "2")
#     # await by.create_order("APEUSDT","Sell","Market", 1, "2")
#     result = await by.get_position_info(symbol="APEUSDT")
#     return result
    
# async def test():
#     result = await close_trade()
#     print(result)
#     d = result['result']['list'][0]['positionIdx']
#     main_leverage = None
#     secondary = None
#     if d == 0:
#         print("Test 1")
#         main_leverage = result['result']['list'][0]['leverage']
#     elif d == 1:
#         print("Test 1")
#         main_leverage = main_leverage
#         secondary = result['result']['list'][1]['leverage']
#     elif d == 2:
#         print("Test 2")
#         main_leverage = result['result']['list'][1]['leverage']  
#         secondary = main_leverage
    
#     print(main_leverage)
#     print(secondary)

# asyncio.run(test())


# sleep(10)