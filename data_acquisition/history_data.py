import requests
import datetime


class HistoryData:
    symbol = None
    interval = None
    end_time = None
    klines = None
    limit = 1000
    start_time = None

    def __init__(self, symbol, interval, cicles = 3):
        self.symbol = symbol
        self.interval = interval

        self.klines = self.get_binance_klines(self.symbol, self.interval, self.end_time, self.limit)
        for i in range(cicles - 1):
            # print(len(self.klines))
            self.klines = self.get_binance_klines(self.symbol, self.interval,self.get_current_oldest_time_minus_one(), self.limit) + self.klines

        # print(self.klines[0][0])
        # print(self.klines[len(self.klines) - 1][0])
        # print(len(self.klines))

    def get_current_oldest_time_minus_one(self):    
        datetime_obj_one = datetime.datetime.fromtimestamp(
            self.klines[0][0] / 1000)
        datetime_obj_two = datetime.datetime.fromtimestamp(
            self.klines[1][0] / 1000)
        return self.subtract_datetime_difference(datetime_obj_one, datetime_obj_two)
    
    def get_last_candles(self,symbol,interval,limit):
        return self.get_binance_klines(symbol,interval,None,limit)

    def subtract_datetime_difference(_, datetime1, datetime2):
        # Calculate the date difference
        date_difference = (datetime2.date() - datetime1.date()).days

        # Calculate the time difference
        time_difference = datetime2 - datetime1
        if datetime1 > datetime2:
            time_difference = datetime.timedelta(
                days=0, seconds=time_difference.seconds)

        # Subtract the date and time differences
        result = datetime1 - \
            datetime.timedelta(days=date_difference) - time_difference
        
        

        return int(result.timestamp() * 1000)

    @staticmethod
    def get_binance_klines(symbol, interval, end_time, limit):
        base_url = 'https://api.binance.com'
        endpoint = '/api/v3/uiKlines'

        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }

        # if start_time is not None:
        #     params['startTime'] = start_time

        if end_time is not None:
            params['endTime'] = end_time

        response = requests.get(base_url + endpoint, params=params)
        data = response.json()
        # print(data)
        return data

# import pandas as pd
   
# data = HistoryData(symbol="BTCUSDT", interval="5m", cicles= 3)
# df = pd.DataFrame(data.klines, columns=["k_open_time", "open_price", "high_price", "low_price", "close_price", "volume",
#                                                           "k_close_time", "quote_asset_volume", "number_Trades", "taker_buy_base_asset_volume",
#                                                           "taker_buy_quote_asset_volume", "ignore"])

# print(len(df))