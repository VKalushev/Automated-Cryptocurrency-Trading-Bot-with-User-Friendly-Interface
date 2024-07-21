import requests
import datetime


class BybitHistoryData:
    symbol = None
    interval = None
    end_time = None
    klines = None
    limit = 1000
    start_time = None

    def __init__(self,category,symbol, interval, cicles = 3):
        self.category = category
        self.symbol = symbol
        self.interval = interval

        self.klines = self.get_bybit_klines(category,self.symbol, self.interval, self.end_time, self.limit)
        self.klines = self.klines['result']['list']
        self.klines.reverse()

        for i in range(cicles - 1):
            new_kline = self.get_bybit_klines(category,self.symbol, self.interval,self.get_current_oldest_time_minus_one(), self.limit)
            new_kline = new_kline['result']['list']
            new_kline.reverse()
            self.klines = new_kline + self.klines


    def get_current_oldest_time_minus_one(self):
        datetime_obj_one = datetime.datetime.fromtimestamp(
            int(self.klines[0][0]) / 1000)
        # print("[0]",str(datetime_obj_one))
        datetime_obj_two = datetime.datetime.fromtimestamp(
            int(self.klines[1][0]) / 1000)
        # print("[1]",str(datetime_obj_two))
        return self.subtract_datetime_difference(datetime_obj_one, datetime_obj_two)

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
    def get_bybit_klines(category,symbol, interval, end_time, limit):
        base_url = 'https://api.bybit.com'
        endpoint = '/v5/market/kline'

        params = {
            'category': category,
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
# data = BybitHistoryData(category="linear",symbol="BTCUSDT", interval="1", cicles= 3)
# df = pd.DataFrame(data.klines, columns=["open_time", "open_price", "high_price", "low_price", "close_price", "volume", "turnover"])
# datetime_obj_one = datetime.datetime.fromtimestamp(int(df.iloc[0]['open_time']) / 1000)
# print("[0]",str(datetime_obj_one))
# datetime_obj_one = datetime.datetime.fromtimestamp(int(df.iloc[999]['open_time']) / 1000)
# print("[999]",str(datetime_obj_one))
# datetime_obj_one = datetime.datetime.fromtimestamp(int(df.iloc[1000]['open_time']) / 1000)
# print("[1000]",str(datetime_obj_one))
# datetime_obj_one = datetime.datetime.fromtimestamp(int(df.iloc[1999]['open_time']) / 1000)
# print("[1999]",str(datetime_obj_one))
# datetime_obj_one = datetime.datetime.fromtimestamp(int(df.iloc[2000]['open_time']) / 1000)
# print("[2000]",str(datetime_obj_one))
# datetime_obj_one = datetime.datetime.fromtimestamp(int(df.iloc[2999]['open_time']) / 1000)
# print("[2999]",str(datetime_obj_one))
