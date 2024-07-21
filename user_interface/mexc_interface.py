from user_interface.main_interface import MainInterface
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QLabel
from user_interface.graph_widget import GraphWidget
import plotly.io as pio

class MexcUserInterface(MainInterface):
    def __init__(self, database,user_data,symbol="BTCUSDT",interval="1m"):
        super().__init__(database,user_data,symbol,interval)
        print("TODO MEXC INTERFACE")
        print("TODO MEXC INTERFACE")
        print("TODO MEXC INTERFACE")
        print("TODO MEXC INTERFACE")

    
    def handle_pnl_labels(self,data):
        if('result' in data):
            current_data_list = data['result']['list']

            for data in current_data_list:
                # print(data)
                symbol = data['symbol']
                ordered_quantity = data['qty']
                entry_price = data['avgEntryPrice']
                exit_price = data['avgExitPrice']
                side = data['side']
                closed_pnl = float(data['closedPnl'])
                creation_time = data['createdTime']

                creation_time = self.convert_time(creation_time)
                open_fee = (float(entry_price)*float(ordered_quantity)) * 0.00055
                closed_fee = (float(entry_price)*float(ordered_quantity)) * 0.00055
                total_fee = open_fee + closed_fee

                closed_pnl = "{:.3f}".format(closed_pnl)
                open_fee = "{:.4f}".format(open_fee)
                closed_fee = "{:.4f}".format(closed_fee)
                total_fee = "{:.4f}".format(total_fee)

                
                symbol_label = QLabel(symbol)
                ordered_quantity_label = QLabel(ordered_quantity)
                entry_price_label = QLabel(entry_price)
                exit_price_label = QLabel(exit_price)
                trade_type_label = QLabel(side)
                closed_pnl_label = QLabel(closed_pnl)
                open_fee_label = QLabel(open_fee)
                close_fee_label = QLabel(closed_fee)
                total_fee_label = QLabel(total_fee)
                creation_time_label = QLabel(creation_time)

                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.addWidget(symbol_label)
                layout.addWidget(ordered_quantity_label)
                layout.addWidget(entry_price_label)
                layout.addWidget(exit_price_label)
                layout.addWidget(trade_type_label)
                layout.addWidget(closed_pnl_label)
                layout.addWidget(open_fee_label)
                layout.addWidget(close_fee_label)
                layout.addWidget(total_fee_label)
                layout.addWidget(creation_time_label)
                self.container_layout.addWidget(widget)

    def handle_current_orders_labels(self,data):
        if('result' in data):

            current_data_list = data['result']['list']

            for data in current_data_list:
                # print(data)
                symbol = data['symbol']
                ordered_quantity = data['qty']
                order_price = data['price']
                stop_loss = data['stopLoss']
                take_profit = data['takeProfit']
                order_type = data['orderType']
                order_status = data['orderStatus']
                filled_quantity = data['cumExecQty']
                creation_time = data['createdTime']
                side = data['side']

                creation_time = self.convert_time(creation_time)
                
                symbol_label = QLabel(symbol)
                ordered_quantity_label = QLabel(ordered_quantity)
                orderd_price = QLabel(order_price)
                quanitity_label = QLabel(f"{filled_quantity}/{ordered_quantity}")
                take_profit_stop_loss = QLabel(f"{take_profit}/{stop_loss}")
                trade_type_label = QLabel(side)
                order_type_label = QLabel(order_type)
                order_status_label = QLabel(order_status)
                creation_time_label = QLabel(creation_time)

                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.addWidget(symbol_label)
                layout.addWidget(ordered_quantity_label)
                layout.addWidget(orderd_price)
                layout.addWidget(quanitity_label)
                layout.addWidget(take_profit_stop_loss)
                layout.addWidget(trade_type_label)
                layout.addWidget(order_type_label)
                layout.addWidget(order_status_label)
                layout.addWidget(creation_time_label)
                self.container_layout.addWidget(widget)

    def handle_order_history_labels(self,data):
        current_data_list = data['result']['list']
        for data in current_data_list:
            # print(data)
            symbol = data['symbol']
            order_type = data['orderType']
            avg_Price = data['avgPrice']
            order_status = data['orderStatus']
            trade_value = data['cumExecValue']
            creation_time = data['createdTime']
            side = data['side']
            quantity_purchased = data['qty']

            creation_time = self.convert_time(creation_time)

            if(order_status != 'Deactivated'):
                symbol_label = QLabel(symbol)
                quanitity_label = QLabel(f"{quantity_purchased}/{order_type}")
                avg_price_label = QLabel(avg_Price)
                order_status_label = QLabel(order_status)
                trade_value_label = QLabel(trade_value)
                creation_time_label = QLabel(creation_time)
                buy_or_sell_label = QLabel(side)

                widget = QWidget()
                layout = QHBoxLayout(widget)

                layout.addWidget(symbol_label)
                layout.addWidget(buy_or_sell_label)
                layout.addWidget(quanitity_label)
                layout.addWidget(avg_price_label)
                layout.addWidget(trade_value_label)
                layout.addWidget(order_status_label)
                layout.addWidget(creation_time_label)
                self.container_layout.addWidget(widget)


    def handle_trade_history_labels(self,data):
        current_data_list = data['result']['list']
        for data in current_data_list:
            # print(data)
            symbol = data['symbol']
            order_type = data['orderType']
            avg_Price = data['execPrice']
            trade_value = data['execValue']
            creation_time = data['execTime']
            side = data['side']
            quantity_purchased = data['orderQty']
            execution_fee = data['execFee']

            creation_time = self.convert_time(creation_time)

            symbol_label = QLabel(symbol)
            quanitity_label = QLabel(f"{quantity_purchased}/{order_type}" )
            avg_price_label = QLabel(avg_Price)
            execution_fee_label = QLabel(execution_fee)
            trade_value_label = QLabel(trade_value)
            creation_time_label = QLabel(creation_time)
            buy_or_sell_label = QLabel(side)

            widget = QWidget()
            layout = QHBoxLayout(widget)

            layout.addWidget(symbol_label)
            layout.addWidget(quanitity_label)
            layout.addWidget(avg_price_label)
            layout.addWidget(trade_value_label)
            layout.addWidget(buy_or_sell_label)
            layout.addWidget(execution_fee_label)
            layout.addWidget(creation_time_label)
            self.container_layout.addWidget(widget)

    def update_chart(self, data):
        print(data)
        if(data['data'][0]['confirm']):
            new_data = []
            new_data.append(int(data['data'][0]['start']))
            new_data.append(float(data['data'][0]['open']))
            new_data.append(float(data['data'][0]['high']))
            new_data.append(float(data['data'][0]['low']))
            new_data.append(float(data['data'][0]['close']))
            new_data.append(float(data['data'][0]['volume']))
            new_data.append(int(data['data']['k']['end']))
            new_data.append(float(data['data']['k']['turnover']))
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
        if('result' not in data):
            self.update_ballance_labels(data['data'])

    def set_account_balance(self,data):
        margin_balance_value = "{:.2f}".format(float(data['result']['list'][0]['coin'][0]['walletBalance']))
        available_balance_label_number = "{:.2f}".format(float(data['result']['list'][0]['coin'][0]['availableToWithdraw']))
        self.margin_balance_label_number.setText(margin_balance_value)
        self.available_balance_label_number.setText(available_balance_label_number)

    def update_ballance_labels(self,data):
        margin_balance_value = "{:.2f}".format(float(data[0]['coin'][1]['walletBalance']))
        available_balance_label_number = "{:.2f}".format(float(data[0]['coin'][1]['availableToWithdraw']))
        self.margin_balance_label_number.setText(margin_balance_value)
        self.available_balance_label_number.setText(available_balance_label_number)

    def changeCoin(self, coin_name):
        print("TODO changeCoin MEXC")
        print("TODO changeCoin MEXC")
        print("TODO changeCoin MEXC")
        print("TODO changeCoin MEXC")
        print("TODO changeCoin MEXC")
        print("TODO changeCoin MEXC")
        print("TODO changeCoin MEXC")

    def change_graph_interval(self,new_interval):
        print("TODO change_graph_interval MEXC")
        print("TODO change_graph_interval MEXC")
        print("TODO change_graph_interval MEXC")
        print("TODO change_graph_interval MEXC")
        print("TODO change_graph_interval MEXC")
        print("TODO change_graph_interval MEXC")
        print("TODO change_graph_interval MEXC")

