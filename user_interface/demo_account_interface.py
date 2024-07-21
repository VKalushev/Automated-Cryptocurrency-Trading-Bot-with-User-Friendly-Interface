from user_interface.main_interface import MainInterface
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QLabel
from user_interface.graph_widget import GraphWidget
import plotly.io as pio

class DemoUserInterface(MainInterface):
    def __init__(self, database,user_data ,symbol="BTCUSDT", interval="1"):
        super().__init__(database,user_data ,symbol, interval)

    def create_graph_widget(self):
        return GraphWidget(symbol=self.symbol, interval=self.interval, end_time=None)
    
    def handle_pnl_labels(self,data):
        pass

    def handle_current_orders_labels(self,data):
        pass

    def handle_order_history_labels(self,data):
        pass


    def handle_trade_history_labels(self,data):
        pass

    def update_chart(self, data):
        if(data['data'][0]['confirm']):
            new_data = []
            new_data.append(int(data['data'][0]['start']))
            new_data.append(float(data['data'][0]['open']))
            new_data.append(float(data['data'][0]['high']))
            new_data.append(float(data['data'][0]['low']))
            new_data.append(float(data['data'][0]['close']))
            new_data.append(float(data['data'][0]['volume']))
            new_data.append(float(data['data'][0]['turnover']))
            self.trading_graph.update_fig(new_data)
            # Update the existing QWebEngineView with the new HTML content
            html_string = pio.to_html(self.trading_graph.fig, include_plotlyjs='cdn')
            self.web_view.setHtml(html_string)

    def update_ticker_labels(self, data):
        if('result' not in data):
            data = data['data']
            current_price = "{:.2f}".format(float(data["lastPrice"]))
            daily_change = "{:.2f}".format(float(data["price24hPcnt"]))
            daily_high = "{:.2f}".format(float(data["highPrice24h"]))
            daily_low = "{:.2f}".format(float(data["lowPrice24h"]))
            daily_volume = "{:.2f}".format(float(data["turnover24h"]))

            self.coin_price_label_number.setText(current_price)
            self.coin_price_change_prct_label_number.setText(daily_change)
            self.coin_daily_high_price_label_number.setText(daily_high)
            self.coin_daily_low_price_label_number.setText(daily_low)
            self.coin_daily_volume_label_number.setText(daily_volume)

    def handle_position_data(self,data):
        current_data = data['result']['list'][0]

        return current_data

    def update_wallet_data(self,data):
        pass

    def set_account_balance(self,data):
        pass

    def update_ballance_labels(self,data):
        pass
