from PyQt5.QtWidgets import QHBoxLayout, QWidget, QLabel, QPushButton
from PyQt5.QtCore import pyqtSignal,QObject
from datetime import datetime

class ActivePositionWidget(QWidget,QObject):
    emitter_close_position = pyqtSignal(object)

    def __init__(self, data,parent=None):
        super().__init__(parent)
        # print(data)
        self.symbol = data['symbol']
        self.entry_price = data['avgPrice']
        self.liq_price = data['liqPrice']
        self.take_profit = data['takeProfit']
        self.stop_loss = data['stopLoss']
        self.side = data['side']
        self.unrealized_pnl = data['unrealisedPnl']
        self.market_price = data['markPrice']
        self.updated_time = data['updatedTime']
        self.trade_value = data['positionValue']
        self.position_size = data['size']
        self.position_index = data['positionIdx']

        creation_time = self.convert_time(self.updated_time)

        self.symbol_label_active_position = QLabel(self.symbol)
        self.trade_type_label_active_position = QLabel(self.side)
        self.ordered_quantity_label_active_position = QLabel(self.position_size)
        self.trade_value_active_position = QLabel(self.trade_value)
        self.entry_price_active_position = QLabel(self.entry_price)
        self.market_price_active_position = QLabel(self.market_price)
        self.liquidation_price_active_position = QLabel(self.liq_price)
        self.unrialized_pnl_active_position = QLabel(self.unrealized_pnl)
        self.take_profit_stop_loss_active_position = QLabel(f"{self.take_profit}/{self.stop_loss}")
        self.order_time_active_position = QLabel(creation_time)
        self.close_position = QPushButton("Close")
        self.close_position.clicked.connect(self.close_button_clicked)

        # widget = QWidget()
        layout = QHBoxLayout(self)
        layout.addWidget(self.symbol_label_active_position)
        layout.addWidget(self.trade_type_label_active_position)
        layout.addWidget(self.ordered_quantity_label_active_position)
        layout.addWidget(self.trade_value_active_position)
        layout.addWidget(self.entry_price_active_position)
        layout.addWidget(self.market_price_active_position)
        layout.addWidget(self.liquidation_price_active_position)
        layout.addWidget(self.unrialized_pnl_active_position)
        layout.addWidget(self.take_profit_stop_loss_active_position)
        layout.addWidget(self.order_time_active_position)
        layout.addWidget(self.close_position)

    def update_data(self,data):
        self.symbol = data['symbol']
        self.entry_price = data['avgPrice']
        self.liq_price = data['liqPrice']
        self.take_profit = data['takeProfit']
        self.stop_loss = data['stopLoss']
        self.side = data['side']
        self.unrealized_pnl = data['unrealisedPnl']
        self.market_price = data['markPrice']
        self.updated_time = data['updatedTime']
        self.trade_value = data['positionValue']
        self.position_size = data['size']

        creation_time = self.convert_time(self.updated_time)

        self.symbol_label_active_position.setText(self.symbol)
        self.trade_type_label_active_position.setText(self.side)
        self.ordered_quantity_label_active_position.setText(self.position_size)
        self.trade_value_active_position.setText(self.trade_value)
        self.entry_price_active_position.setText(self.entry_price)
        self.market_price_active_position.setText(self.market_price)
        self.liquidation_price_active_position.setText(self.liq_price)
        self.unrialized_pnl_active_position.setText(self.unrealized_pnl)
        self.take_profit_stop_loss_active_position.setText(f"{self.take_profit}/{self.stop_loss}")
        self.order_time_active_position.setText(creation_time)

    def close_button_clicked(self):
        data = {}
        if self.position_index == 0:
            if self.side == "Buy":
                data = {"symbol": self.symbol, "size": self.position_size, 'side': "Sell", "position_index": self.position_index}
            else:
                data = {"symbol": self.symbol, "size": self.position_size, 'side': "Buy", "position_index": self.position_index}
        else:
            if self.side == "Buy":
                data = {"symbol": self.symbol, "size": self.position_size, 'side': "Sell", "position_index": 1}
            else:
                data = {"symbol": self.symbol, "size": self.position_size, 'side': "Buy", "position_index": 2}


        self.emitter_close_position.emit(data)

    def convert_time(self,time):
        dt_object = datetime.utcfromtimestamp(int(time) / 1000.0)
        year = dt_object.year
        month = dt_object.month
        day = dt_object.day
        hour = dt_object.hour
        minute = dt_object.minute
        sec = dt_object.second

        if(day < 10):
            day = f"0{day}"

        if(month < 10):
            month = f"0{month}"

        if(hour < 10):
            hour = f"0{hour}"

        if(minute < 10):
            minute = f"0{minute}"

        if(sec < 10):
            sec = f"0{sec}"

        return str(f"{year}-{month}-{day} {hour}:{minute}:{sec}")