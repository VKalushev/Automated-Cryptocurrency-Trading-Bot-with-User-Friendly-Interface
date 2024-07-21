import requests
import datetime


class MexcHistoryData:
    symbol = None
    interval = None
    end_time = None
    klines = None
    start_time = None

    def __init__(self,symbol, interval, cicles = 3):
        self.symbol = symbol
        self.interval = interval

        # current_time_ms = int(datetime.datetime.timestamp(datetime.datetime.now()) * 1000)
        klines = self.get_mexc_klines(symbol=self.symbol, interval=self.interval)
        self.klines = self.restructure(klines)
        print(self.klines[0])
        for i in range(cicles - 1):
            print('a')
            new_kline = self.get_mexc_klines(symbol=self.symbol, interval=self.interval,end=self.get_current_oldest_time_minus_one())
            new_kline = self.restructure(new_kline)
            # new_kline.reverse()
            self.klines = new_kline + self.klines

    def restructure(self, klines):
        new_kline = []
        for i in range(len(klines['data']['time'])):
            new_entry = [
                klines['data']['time'][i],
                klines['data']['open'][i],
                klines['data']['close'][i],
                klines['data']['high'][i],
                klines['data']['low'][i],
                klines['data']['vol'][i],
                klines['data']['amount'][i]
            ]
            new_kline.append(new_entry)
        return new_kline


    def get_current_oldest_time_minus_one(self):
        datetime_obj_one = datetime.datetime.fromtimestamp(
            int(self.klines[0][0]))
        print("[0]",str(datetime_obj_one))
        datetime_obj_two = datetime.datetime.fromtimestamp(
            int(self.klines[1][0]))
        print("[1]",str(datetime_obj_two))
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
    
    def get_mexc_klines(self,symbol, interval=None, start=None, end=None):
        base_url = 'https://contract.mexc.com'
        path = '/api/v1/contract/kline'
        path = f'{path}/{symbol}'
        
        if interval:
            path = f'{path}?interval={interval}'
        if start:
            path = f'{path}&start={start}'
        if end:
            path = f'{path}&end={end}'
        url = f'{base_url}/{path}'
        response = requests.request('GET', url)

        return response.json()

    # @staticmethod
    # def get_mexc_klines(symbol, interval, end_time):
    #     base_url = 'https://contract.mexc.com'
    #     endpoint = f'api/v1/contract/kline/{symbol}'

    #     params = {
    #         'symbol': symbol,
    #         'interval': interval,
    #     }

    #     # if start_time is not None:
    #     #     params['startTime'] = start_time

    #     if end_time is not None:
    #         params['endTime'] = end_time

    #     response = requests.get(base_url + endpoint, params=params)
    #     data = response.json()
    #     # print(data)
    #     return data

import pandas as pd

data = MexcHistoryData(symbol="BTC_USDT", interval="Min1", cicles= 3)
df = pd.DataFrame(data.klines, columns=["open_time", "open_price", "close_price", "high_price", "low_price", "volume", "turnover"])
print(df)
# datetime_obj_one = datetime.datetime.fromtimestamp(1707745200 / 1000)
# print("[0]",str(datetime_obj_one))
# datetime_obj_one = datetime.datetime.fromtimestamp(int(df.iloc[0]['open_time']))
# print("[0]",str(datetime_obj_one))
# datetime_obj_one = datetime.datetime.fromtimestamp(int(df.iloc[999]['open_time']))
# print("[999]",str(datetime_obj_one))
# datetime_obj_one = datetime.datetime.fromtimestamp(int(df.iloc[1000]['open_time']))
# print("[1000]",str(datetime_obj_one))
# datetime_obj_one = datetime.datetime.fromtimestamp(int(df.iloc[1999]['open_time']))
# print("[1999]",str(datetime_obj_one))
# # datetime_obj_one = datetime.datetime.fromtimestamp(int(df.iloc[2000]['open_time']))
# print("[2000]",str(datetime_obj_one))
# datetime_obj_one = datetime.datetime.fromtimestamp(int(df.iloc[2999]['open_time']))
# print("[2999]",str(datetime_obj_one))
