from PyQt5.QtWidgets import QVBoxLayout, QWidget
from data_acquisition.bybit_history_data import BybitHistoryData
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import datetime


class GraphWidget(QWidget):
    data = None
    df = None
    symbol = None
    interval = None
    end_time = None
    fig = None

    def __init__(self, symbol, interval, end_time):
        super().__init__()
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.symbol = symbol
        self.interval = interval
        self.end_time = end_time
        
        self.data = BybitHistoryData(category="linear",symbol=symbol, interval=interval)
        self.df = pd.DataFrame(self.data.klines, columns=["open_time", "open_price", "high_price", "low_price", "close_price", "volume", "turnover"])

        # Convert timestamp to datetime object
        timestamps = [datetime.datetime.fromtimestamp(
            int(ts)/1000) for ts in self.df['open_time']]

        self.fig = go.Figure(data=[go.Candlestick(x=timestamps, open=self.df['open_price'],
                                                  high=self.df['high_price'], low=self.df['low_price'],
                                                  close=self.df["close_price"])])
        
        # Formats numbers as integers without decimal places
        open_price = self.df.iloc[0]['open_price']
        if float(open_price) > 1000:
            self.fig.update_yaxes(tickformat=".0f")
        elif float(open_price) > 20:
            self.fig.update_yaxes(tickformat=".2f")
        elif float(open_price) > 1:
            self.fig.update_yaxes(tickformat=".3f")
        else:
            self.fig.update_yaxes(tickformat=".4f")

            

        self.fig.update_layout(
            xaxis_rangeslider_visible=False, template="plotly_dark", yaxis_title=f"{self.symbol}", xaxis_title="Date")
        self.fig.update_yaxes(type="log")

    def create_graph(self,interval,symbol):
        self.symbol = symbol
        self.interval = interval
        
        self.data = BybitHistoryData(category="linear",symbol=symbol, interval=interval)
        self.df = pd.DataFrame(self.data.klines, columns=["open_time", "open_price", "high_price", "low_price", "close_price", "volume", "turnover"])

        # Convert timestamp to datetime object
        timestamps = [datetime.datetime.fromtimestamp(
            int(ts)/1000) for ts in self.df['open_time']]

        self.fig = go.Figure(data=[go.Candlestick(x=timestamps, open=self.df['open_price'],
                                                  high=self.df['high_price'], low=self.df['low_price'],
                                                  close=self.df["close_price"])])
        
        # Formats numbers as integers without decimal places
        open_price = self.df.iloc[0]['open_price']
        if float(open_price) > 1000:
            self.fig.update_yaxes(tickformat=".0f")
        elif float(open_price) > 20:
            self.fig.update_yaxes(tickformat=".2f")
        elif float(open_price) > 1:
            self.fig.update_yaxes(tickformat=".3f")
        else:
            self.fig.update_yaxes(tickformat=".4f")

        self.fig.update_layout(
            xaxis_rangeslider_visible=False, template="plotly_dark", yaxis_title=f"{self.symbol}", xaxis_title="Date")
        self.fig.update_yaxes(type="log")


    def update_fig(self, new_data):
        # Append the newest data as a single candle to the existing graph
        self.df.loc[len(self.df)] = new_data
        
        # Convert timestamp to datetime object
        timestamps = [datetime.datetime.fromtimestamp(
            int(ts)/1000) for ts in self.df['open_time']]
        
        self.fig = go.Figure(data=[go.Candlestick(x=timestamps, open=self.df['open_price'],
                                                  high=self.df['high_price'], low=self.df['low_price'],
                                                  close=self.df["close_price"])])
        
        
        # Formats numbers as integers without decimal places
        open_price = self.df.iloc[0]['open_price']
        if float(open_price) > 1000:
            self.fig.update_yaxes(tickformat=".0f")
        elif float(open_price) > 20:
            self.fig.update_yaxes(tickformat=".2f")
        elif float(open_price) > 1:
            self.fig.update_yaxes(tickformat=".3f")
        else:
            self.fig.update_yaxes(tickformat=".4f")
        self.fig.update_layout(
            xaxis_rangeslider_visible=False, template="plotly_dark", yaxis_title=f"{self.symbol}", xaxis_title="Date")
        self.fig.update_yaxes(type="log")
