from PyQt5.QtCore import pyqtSignal, QObject
import json
import time
import hmac
import hashlib
import requests    
import websocket
import threading

class MEXCWebsocket(QObject):
    BASE_URL = 'wss://contract.mexc.com/edge'
    API_KEY = 'mx0vglMeocWxhcb3eA'
    SECRET_KEY = '2b3906e753b7409591a35431910ea005'

    message_received = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.ws_login = websocket.WebSocketApp(self.BASE_URL,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        self.ws_kline = websocket.WebSocketApp(self.BASE_URL,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        self.ws_login.run_forever()
        self.ws_kline.run_forever()


    def run(self):
        self.ws_login.on_open = self.on_open
        self.ws_login.run_forever()

    def subscribe_kline_data(self):
        params = {
            "method":"sub.kline",
            "param":{
                "symbol":"BTC_USDT",
                "interval":"Min1"
            }
        }

    def on_open(self, ws):
        reqTime = self._get_server_time()
        sign = self._sign_v1()
        params = {
            "method": "login",
            "param": {
                "apiKey": self.API_KEY,
                "reqTime": reqTime,
                "signature": sign,
            }
        }
        print(json.dumps(params))
        self.ws_login.send(json.dumps(params))
        print('Opened ....')
        threading.Thread(target=self.send_ping).start()

    def on_message(self, ws, message):
        print(message)
        self.message_received.emit(message)

    def on_error(self, ws, error):
        print('Connection error ....')
        print(error)

    def on_close(self, ws):
        print("Connection closed ....")

    def _get_server_time(self):
        return int(time.time() * 1000)

    def _sign_v1(self, sign_params=None):
        sign = "%s%s" % (self.API_KEY, self._get_server_time())
        sign = hmac.new(self.SECRET_KEY.encode('utf-8'), sign.encode('utf-8'),
                        hashlib.sha256).hexdigest()
        return sign

    def send_ping(self):
        while self.running:
            time.sleep(30)
            params = {"method": "ping"}
            self.ws_login.send(json.dumps(params))

    def start_connection(self):
        self.running = True
        self.run()

    def stop_connection(self):
        self.running = False
        self.ws_login.close()



class MexcExchange(QObject):
    BASE_URL = 'https://contract.mexc.com'

    def __init__(self,api_key='mx0vglMeocWxhcb3eA',secret_key='2b3906e753b7409591a35431910ea005'):
        super().__init__()
        self.API_KEY = api_key
        self.SECRET_KEY = secret_key
        self.websocket = MEXCWebsocket()
        self.moveToThread(self.ws_thread)
        self.websocket.start_connection()

    def change_keys(self,new_API_KEY,new_SECRET_KEY):
        self.API_KEY = new_API_KEY
        self.SECRET_KEY = new_SECRET_KEY       


    def _get_server_time(self):
        return int(time.time()*1000)

    def _sign_v1(self,sign_params=None):
        if sign_params:
            sign = "%s%s%s" % (self.API_KEY, self._get_server_time(), sign_params)
        else:
            sign = "%s%s" % (self.API_KEY, self._get_server_time())
        sign = hmac.new(self.SECRET_KEY.encode('utf-8'), sign.encode('utf-8'),
                        hashlib.sha256).hexdigest()
        return sign


    def get_ping(self):
        path = '/api/v1/contract/ping'
        url = '{}{}'.format(self.BASE_URL, path)
        response = requests.request('GET', url)
        return response.json()


    def get_contract_detail(self,symbol=None):
        """
        获取合约信息
        :param symbol: 合约名
        :return:
        """
        path = '/api/v1/contract/detail'
        if symbol:
            path = f'{path}?symbol={symbol}'
        url = '{}{}'.format(self.BASE_URL, path)
        response = requests.request('GET', url)
        return response.json()


    def get_depth(self,symbol, limit=None):
        """get depth data"""
        path = '/api/v1/contract/depth'
        path = f'{path}/{symbol}'
        if limit:
            path = f'{path}?limit={limit}'
        url = f'{self.BASE_URL}/{path}'
        response = requests.request('GET', url)
        return response.json()
    # res = get_depth('ETH_USDT', 1)
    # print(res)


    def get_kline(self,symbol, interval=None, start=None, end=None):
        """get k-line data"""
        path = '/api/v1/contract/kline'
        path = f'{path}/{symbol}'
        if interval:
            path = f'{path}?interval={interval}'
        if start:
            path = f'{path}&start={start}'
        if end:
            path = f'{path}&end={end}'
        url = f'{self.BASE_URL}/{path}'
        response = requests.request('GET', url)
        return response.json()
    # res = get_kline('ETH_USDT')
    # print(res)


    def get_account_assets(self):
        """get account information"""
        method = 'GET'
        path = '/api/v1/private/account/assets'
        url = '{}{}'.format(self.BASE_URL, path)
        sign = self._sign_v1()
        headers = {
            "ApiKey": self.API_KEY,
            "Request-Time": str(self._get_server_time()),
            "Signature": sign,
            "Content-Type": "application/json"
        }
        response = requests.request(method, url, headers=headers)
        return response.json()



    def get_account_asset_currency(self,currency):
        """get account information"""
        method = 'GET'
        path = '/api/v1/private/account/asset/' + currency
        url = '{}{}'.format(self.BASE_URL, path)
        sign = self._sign_v1()
        headers = {
            "ApiKey": self.API_KEY,
            "Request-Time": str(self._get_server_time()),
            "Signature": sign,
            "Content-Type": "application/json"
        }
        response = requests.request(method, url, headers=headers)
        return response.json()


    def history_positions(self,page_num, page_size=None, symbol=None):
        """get history positions"""
        method = 'GET'
        path = '/api/v1/private/position/list/history_positions'
        url = '{}{}'.format(self.BASE_URL, path)
        data_original = {
            'page_num': page_num
        }
        if page_size:
            data_original = {"page_size": page_size}
        if symbol:
            data_original = {"symbol": symbol}
        data = '&'.join('{}={}'.format(i, data_original[i]) for i in sorted(data_original))
        sign = self._sign_v1(sign_params=data)
        headers = {
            "ApiKey": self.API_KEY,
            "Request-Time": str(self._get_server_time()),
            "Signature": sign,
            "Content-Type": "application/json"
        }
        url = "%s%s%s" % (url, "?", data)
        response = requests.request(method, url, headers=headers)
        return response.json()



    def get_open_positions(self,symbol=None):
        """get Open Positions"""
        method = 'GET'
        path = '/api/v1/private/position/open_positions'
        url = '{}{}'.format(self.BASE_URL, path)
        if symbol:
            data_original = {"symbol": symbol}
        else:
            data_original = {}
        data = '&'.join('{}={}'.format(i, data_original[i]) for i in sorted(data_original))
        sign = self._sign_v1(sign_params=data)
        headers = {
            "ApiKey": self.API_KEY,
            "Request-Time": str(self._get_server_time()),
            "Signature": sign,
            "Content-Type": "application/json"
        }
        url = "%s%s%s" % (url, "?", data)
        response = requests.request(method, url, headers=headers)
        return response.json()



    def get_position_funding_records(self,page_num=None, page_size=None, symbol=None, position_id=None):
        """get funding records"""
        method = 'GET'
        path = '/api/v1/private/position/funding_records'
        url = '{}{}'.format(self.BASE_URL, path)
        data_original = {}
        if page_num:
            data_original.update({'page_num': page_num})
        if page_size:
            data_original.update({'page_size': page_size})
        if symbol:
            data_original.update({'symbol': symbol})
        if position_id:
            data_original.update({'position_id': position_id})
        data = '&'.join('{}={}'.format(i, data_original[i]) for i in sorted(data_original))
        sign = self._sign_v1(sign_params=data)
        headers = {
            "ApiKey": self.API_KEY,
            "Request-Time": str(self._get_server_time()),
            "Signature": sign,
            "Content-Type": "application/json"
        }
        response = requests.request(method, url, params=data, headers=headers)
        return response.json()


    def get_open_orders(self,page_num=None, page_size=None, symbol=None):
        """get Open Orders"""
        method = 'GET'
        path = '/api/v1/private/order/list/open_orders'
        url = '{}{}'.format(self.BASE_URL, path)
        data_original = {}
        if page_num:
            data_original.update({'page_num': page_num})
        if page_size:
            data_original.update({'page_size': page_size})
        if symbol:
            data_original.update({'symbol': symbol})
        data = '&'.join('{}={}'.format(i, data_original[i]) for i in sorted(data_original))
        sign = self._sign_v1(sign_params=data)
        headers = {
            "ApiKey": self.API_KEY,
            "Request-Time": str(self._get_server_time()),
            "Signature": sign,
            "Content-Type": "application/json"
        }
        response = requests.request(method, url, params=data, headers=headers)
        return response.json()


    def get_history_orders(self,page_num=None, page_size=None, symbol=None, states=None, category=None, start_time=None, end_time=None, side=None):
        """get History Orders"""
        method = 'GET'
        path = '/api/v1/private/order/list/history_orders'
        url = '{}{}'.format(self.BASE_URL, path)
        data_original = {}
        if page_num:
            data_original.update({'page_num': page_num})
        if page_size:
            data_original.update({'page_size': page_size})
        if symbol:
            data_original.update({'symbol': symbol})
        if states:
            data_original.update({'states': states})
        if category:
            data_original.update({'category': category})
        if start_time:
            data_original.update({'start_time': start_time})
        if end_time:
            data_original.update({'end_time': end_time})
        if side:
            data_original.update({'side': side})
        data = '&'.join('{}={}'.format(i, data_original[i]) for i in sorted(data_original))
        sign = self._sign_v1(sign_params=data)
        headers = {
            "ApiKey": self.API_KEY,
            "Request-Time": str(self._get_server_time()),
            "Signature": sign,
            "Content-Type": "application/json"
        }
        response = requests.request(method, url, params=data, headers=headers)
        return response.json()


    def get_orders_by_external(self,symbol, external_oid):
        """get orders by external_id"""
        method = 'GET'
        path = '/api/v1/private/order/external'
        url = '{}{}'.format(self.BASE_URL, path)
        data_original = {
            'symbol': symbol,
            'external_oid': external_oid
        }
        data = '&'.join('{}={}'.format(i, data_original[i]) for i in sorted(data_original))
        sign = self._sign_v1(sign_params=data)
        headers = {
            "ApiKey": self.API_KEY,
            "Request-Time": str(self._get_server_time()),
            "Signature": sign,
            "Content-Type": "application/json"
        }
        response = requests.request(method, url, params=data, headers=headers)
        return response.json()


    def get_orders_by_orderId(self,order_id):
        """get orders by order_id"""
        method = 'GET'
        path = '/api/v1/private/order/get/' + order_id
        url = '{}{}'.format(self.BASE_URL, path)
        sign = self._sign_v1()
        headers = {
            "ApiKey": self.API_KEY,
            "Request-Time": str(self._get_server_time()),
            "Signature": sign,
            "Content-Type": "application/json"
        }
        response = requests.request(method, url, headers=headers)
        return response.json()


    def get_orders_deals(self,symbol, page_num=None, page_size=None, start_time=None, end_time=None):
        """get order deals"""
        method = 'GET'
        path = '/api/v1/private/order/list/order_deals'
        url = '{}{}'.format(self.BASE_URL, path)
        data_original = {
            'symbol': symbol,
        }
        if page_num:
            data_original.update({'page_num': page_num})
        if page_size:
            data_original.update({'page_size': page_size})
        if start_time:
            data_original.update({'start_time': start_time})
        if end_time:
            data_original.update({'end_time': end_time})
        data = '&'.join('{}={}'.format(i, data_original[i]) for i in sorted(data_original))
        sign = self._sign_v1(sign_params=data)
        headers = {
            "ApiKey": self.API_KEY,
            "Request-Time": str(self._get_server_time()),
            "Signature": sign,
            "Content-Type": "application/json"
        }
        response = requests.request(method, url, params=data, headers=headers)
        return response.json()

    # under maintenance
    def post_place(self,symbol, price, vol, side, type, openType, leverage=None, positionId=None, externalOid=None, stopLossPrice=None, takeProfitPrice=None, positionMode=None, reduceOnlt=None):
        """place new order"""
        method = 'POST'
        path = '/api/v1/private/order/submit'
        url = '{}{}'.format(self.BASE_URL, path)
        data_original = {
            'symbol': symbol,
            'price': price,
            'vol': vol,
            'side': side,
            'type': type,
            'openType': openType
        }
        if leverage:
            data_original.update({"leverage": leverage})
        if positionId:
            data_original.update({"positionId": positionId})
        if externalOid:
            data_original.update({"externalOid": externalOid})
        if stopLossPrice:
            data_original.update({"stopLossPrice": stopLossPrice})
        if takeProfitPrice:
            data_original.update({"takeProfitPrice": takeProfitPrice})
        if positionMode:
            data_original.update({"positionMode": positionMode})
        if reduceOnlt:
            data_original.update({"reduceOnlt": reduceOnlt})
        data = json.dumps(data_original)
        params = self._sign_v1(sign_params=data)
        headers = {
            "ApiKey": self.API_KEY,
            "Request-Time": str(self._get_server_time()),
            "Signature": params,
            "Content-Type": "application/json"
        }
        response = requests.request(
            method, url, data=data, headers=headers)
        return response.json()
    
# data = MexcExchange()
# asd = data.get_account_assets()
# asd = data.get_user_positions_history()
# asd = data.post_place('ETH_USDT', side=3,openType=2,type=1,vol=1,leverage=175,price=2500)
# asd = data.post_place('ETH_USDT')
# res = data.post_place(symbol='BTC_USDT', price='20000', vol='1', side=1, type=1, openType=2)
# print(res)
# print(asd)
