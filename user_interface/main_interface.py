from PyQt5.QtWidgets import QVBoxLayout,QGridLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QDoubleSpinBox, QAbstractSpinBox,QScrollArea,QMessageBox,QMenu
from PyQt5.QtCore import Qt,pyqtSignal,QObject
from PyQt5 import QtGui
from PyQt5.QtWebEngineWidgets import QWebEngineView
from user_interface.settings_window import SettingsWindow
from user_interface.active_position_widget import ActivePositionWidget
from user_interface.trading_settings_window import TradingSettingsWindow
from datetime import datetime
import plotly.io as pio
import math

class MainInterface(QObject):
    symbol = None
    interval = None
    emitter_buy_order = pyqtSignal(object)
    emitter_sell_order = pyqtSignal(object)
    emitter_close_position = pyqtSignal(object)
    emitter_change_coin_graph = pyqtSignal(object)
    emitter_change_interval_graph = pyqtSignal(object)
    emitter_update_trading_settings = pyqtSignal(object)
    emitter_open_main_window = pyqtSignal(object)
    emitter_update_data = pyqtSignal(object)
    emitter_logout = pyqtSignal(object)

    def __init__(self,database,user_data,symbol, interval):
        super().__init__()
        self.user_data = user_data
        self.user_id = user_data['_id']
        self.active_positions = []
        self.symbol_min_qty = 0
        self.posIdxInfo = 0
        self.max_qty = 0 
        self.symbol = symbol
        self.interval = interval
        self.leverage_main = 10
        self.leverage_secondary = None
        self.last_price = 0
        self.database = database
        self.max_leverage = 100
        self.setup_main_window()
        self.setup_main_window_positioning()
        self.setup_main_window_css()
        
    def setup_main_window(self):
        self.central_widget = QWidget()

        self.is_position_layout_created = False
        self.gridLayout_main = QGridLayout()

        #Section 1: Row # 1 - Coin Data(Left) + Account(Setting + Data (Right))
        self.coin_data_widget = QWidget()  # Create a widget to encapsulate the layout
        # self.coin_data_layout = QHBoxLayout(self.coin_data_widget)
        self.coin_data_layout = QGridLayout(self.coin_data_widget)

        self.coin_data_grid_widget = QWidget()  # Create a widget to encapsulate the layout
        self.coin_data_grid = QGridLayout(self.coin_data_grid_widget)

        # self.coin_name_label = QLabel('BTCUSDT')
        self.chosen_coin_menu_button = QPushButton("BTCUSDT")
        self.coin_menu = QMenu(self.chosen_coin_menu_button)
        self.coin_menu.addAction("BTCUSDT")
        self.coin_menu.addAction("SOLUSDT")
        self.coin_menu.addAction("ETHUSDT")
        self.coin_menu.addAction("DOGEUSDT")
        self.coin_menu.addAction("APEUSDT")
        self.coin_menu.addAction("ADAUSDT")
        self.coin_menu.addAction("XRPUSDT")
        self.coin_menu.addAction("DOTUSDT")
        self.coin_menu.addAction("BNBUSDT")
        self.coin_menu.addAction("ATOMUSDT")

        # Connect the triggered signal of the coin menu actions to the changeCoin function
        for action in self.coin_menu.actions():
            action.triggered.connect(lambda checked, text=action.text(): self.changeCoin(text))
        self.chosen_coin_menu_button.setMenu(self.coin_menu)
        self.coin_price_label_number = QLabel('PRICE')
        self.coin_price_change_prct_label = QLabel('24h Change')
        self.coin_price_change_prct_label_number = QLabel('PRCT CHANGE')
        self.coin_daily_high_price_label = QLabel('24h High')
        self.coin_daily_high_price_label_number = QLabel('HIGH')
        self.coin_daily_low_price_label = QLabel('24h Low')
        self.coin_daily_low_price_label_number = QLabel('LOW')
        self.coin_daily_volume_label = QLabel('Volume is USDT')
        self.coin_daily_volume_label_number = QLabel('VOLUME')

        self.coin_data_grid.addWidget(self.coin_price_change_prct_label,0,2)
        self.coin_data_grid.addWidget(self.coin_price_change_prct_label_number,1,2)
        self.coin_data_grid.addWidget(self.coin_daily_high_price_label,0,3)
        self.coin_data_grid.addWidget(self.coin_daily_high_price_label_number,1,3)
        self.coin_data_grid.addWidget(self.coin_daily_low_price_label,0,4)
        self.coin_data_grid.addWidget(self.coin_daily_low_price_label_number,1,4)
        self.coin_data_grid.addWidget(self.coin_daily_volume_label,0,5)
        self.coin_data_grid.addWidget(self.coin_daily_volume_label_number,1,5)

        self.coin_data_layout.addWidget(self.chosen_coin_menu_button,0,0)
        self.coin_data_layout.addWidget(self.coin_price_label_number,0,1)
        self.coin_data_layout.addWidget(self.coin_data_grid_widget,0,2,1,5)

        self.account_data_widget = QWidget()
        self.account_data_layout = QVBoxLayout(self.account_data_widget)

        self.menu_button = QPushButton(self.user_data['username'])
        self.menu = QMenu(self.menu_button)
        self.menu.addAction("Settings", self.open_settings_window)
        self.menu.addAction("Logout", self.logout)
        self.menu_button.setMenu(self.menu)
        self.account_data_layout.addWidget(self.menu_button)

        self.timeframe_widget = QWidget()
        self.timeframe_layout = QHBoxLayout(self.timeframe_widget)
    	
        self.timeframe_label = QLabel('Timeframe:')
        self.one_minute_timeframe_button = QPushButton("1m")
        self.one_minute_timeframe_button.setCheckable(True)
        self.one_minute_timeframe_button.setChecked(True)

        self.five_minute_timeframe_button = QPushButton("5m")
        self.five_minute_timeframe_button.setCheckable(True)
        self.five_minute_timeframe_button.setChecked(False)

        self.fiveteen_minutes_timeframe_button = QPushButton("15m")
        self.fiveteen_minutes_timeframe_button.setCheckable(True)
        self.fiveteen_minutes_timeframe_button.setChecked(False)

        self.thiry_minutes_timeframe_button = QPushButton("30m")
        self.thiry_minutes_timeframe_button.setCheckable(True)
        self.thiry_minutes_timeframe_button.setChecked(False)

        self.one_hour_timeframe_button = QPushButton("1h")
        self.one_hour_timeframe_button.setCheckable(True)
        self.one_hour_timeframe_button.setChecked(False)

        self.four_hours_timeframe_button = QPushButton("4h")
        self.four_hours_timeframe_button.setCheckable(True)
        self.four_hours_timeframe_button.setChecked(False)

        self.one_day_timeframe_button = QPushButton("1D")
        self.one_day_timeframe_button.setCheckable(True)
        self.one_day_timeframe_button.setChecked(False)

        self.one_week_timeframe_button = QPushButton("1W")
        self.one_week_timeframe_button.setCheckable(True)
        self.one_week_timeframe_button.setChecked(False)

        self.one_month_timeframe_button = QPushButton("1M")
        self.one_month_timeframe_button.setCheckable(True)
        self.one_month_timeframe_button.setChecked(False)

        self.one_minute_timeframe_button.clicked.connect(lambda: self.timeframe_button_clicked("1m"))
        self.five_minute_timeframe_button.clicked.connect(lambda: self.timeframe_button_clicked("5m"))
        self.fiveteen_minutes_timeframe_button.clicked.connect(lambda: self.timeframe_button_clicked("15m"))
        self.thiry_minutes_timeframe_button.clicked.connect(lambda: self.timeframe_button_clicked("30m"))
        self.one_hour_timeframe_button.clicked.connect(lambda: self.timeframe_button_clicked("1h"))
        self.four_hours_timeframe_button.clicked.connect(lambda: self.timeframe_button_clicked("4h"))
        self.one_day_timeframe_button.clicked.connect(lambda: self.timeframe_button_clicked("1D"))
        self.one_week_timeframe_button.clicked.connect(lambda: self.timeframe_button_clicked("1W"))
        self.one_month_timeframe_button.clicked.connect(lambda: self.timeframe_button_clicked("1M"))

        self.timeframe_layout.addWidget(self.timeframe_label)
        self.timeframe_layout.addWidget(self.one_minute_timeframe_button)
        self.timeframe_layout.addWidget(self.five_minute_timeframe_button)
        self.timeframe_layout.addWidget(self.fiveteen_minutes_timeframe_button)
        self.timeframe_layout.addWidget(self.thiry_minutes_timeframe_button)
        self.timeframe_layout.addWidget(self.one_hour_timeframe_button)
        self.timeframe_layout.addWidget(self.four_hours_timeframe_button)
        self.timeframe_layout.addWidget(self.one_day_timeframe_button)
        self.timeframe_layout.addWidget(self.one_week_timeframe_button)
        self.timeframe_layout.addWidget(self.one_month_timeframe_button)

        self.coin_data_layout.addWidget(self.timeframe_widget,1,0,1,7)
        self.gridLayout_main.addWidget(self.coin_data_widget,0,0)
        self.gridLayout_main.addWidget(self.account_data_widget,0,1)

        #Section 2: Row # 2 - Graph(LEFT 75%) + Wallet + Entry Buttons(Settings + Data (Right))
        #LEFT SIDE ----------------------------------------------------------------------------
        self.second_row_left_side_graph_widget = QWidget()
        self.second_row_left_side_graph_layout = QVBoxLayout(self.second_row_left_side_graph_widget)

        self.trading_graph = self.create_graph_widget()
        self.df = self.trading_graph.df

        html_string = pio.to_html(self.trading_graph.fig, include_plotlyjs='cdn')

        self.web_view = QWebEngineView()
        self.web_view.setHtml(html_string)
    
        self.second_row_left_side_graph_layout.addWidget(self.web_view)
        self.gridLayout_main.addWidget(self.second_row_left_side_graph_widget, 1, 0)

        #RIGHT SIDE Row #1 --------------------------------------------------------------------------------------------
        self.second_row_right_side_grid_widget = QWidget()
        self.second_row_right_side_layout = QVBoxLayout(self.second_row_right_side_grid_widget)

        self.second_row_right_side_first_row_grid_widget = QWidget()
        self.second_row_right_side_first_row_grid_layout = QGridLayout(self.second_row_right_side_first_row_grid_widget)



        #FIRST INNER ROW ----------------------------------------------------------------------------------------------
        self.trade_settings_button = QPushButton("Trade Settings")
        self.leverage_label = QPushButton(str(self.leverage_main))
        self.trade_settings_button.clicked.connect(self.open_trade_settings_window)

        self.second_row_right_side_first_row_grid_layout.addWidget(self.trade_settings_button,0,0)
        self.second_row_right_side_first_row_grid_layout.addWidget(self.leverage_label,0,1)

        self.button_limit_order = QPushButton("Limit")
        self.button_market_order = QPushButton("Market")
        self.button_limit_order.setCheckable(True)
        self.button_market_order.setCheckable(True)
        self.button_market_order.setChecked(True)
        self.button_limit_order.clicked.connect(self.limit_button_clicked)
        self.button_market_order.clicked.connect(self.market_button_clicked)
        # self.label_leverage = QLabel("TODO")

        self.second_row_right_side_first_row_grid_layout.addWidget(self.button_limit_order,1,0)
        self.second_row_right_side_first_row_grid_layout.addWidget(self.button_market_order,1,1)
        # self.second_row_right_side_first_row_grid_layout.addWidget(self.label_leverage,0,2)

        #SECOND INNER ROW --------------------------------------------------------------------------------------------
        self.spin_box = QDoubleSpinBox()
        self.percentage_buttons_widget = QWidget()
        self.percentage_buttons_layout = QHBoxLayout(self.percentage_buttons_widget)

        self.ten_percentent_button = QPushButton("10%")
        self.twenty_five_percentent_button = QPushButton("25%")
        self.fifty_percentent_button = QPushButton("50%")
        self.seventy_five_percentent_button = QPushButton("75%")
        self.one_hundred_percentent_button = QPushButton("100%")

        self.ten_percentent_button.setCheckable(True)
        self.twenty_five_percentent_button.setCheckable(True)
        self.fifty_percentent_button.setChecked(True)
        self.seventy_five_percentent_button.setChecked(True)
        self.one_hundred_percentent_button.setChecked(True)

        self.ten_percentent_button.clicked.connect(lambda : self.percent_button_clicked(10))
        self.twenty_five_percentent_button.clicked.connect(lambda : self.percent_button_clicked(25))
        self.fifty_percentent_button.clicked.connect(lambda : self.percent_button_clicked(50))
        self.seventy_five_percentent_button.clicked.connect(lambda : self.percent_button_clicked(75))
        self.one_hundred_percentent_button.clicked.connect(lambda : self.percent_button_clicked(100))

        self.percentage_buttons_layout.addWidget(self.ten_percentent_button)
        self.percentage_buttons_layout.addWidget(self.twenty_five_percentent_button)
        self.percentage_buttons_layout.addWidget(self.fifty_percentent_button)
        self.percentage_buttons_layout.addWidget(self.seventy_five_percentent_button)
        self.percentage_buttons_layout.addWidget(self.one_hundred_percentent_button)

        self.second_row_right_side_first_row_grid_layout.addWidget(self.spin_box,2,0,1,2)
        self.second_row_right_side_first_row_grid_layout.addWidget(self.percentage_buttons_widget,3,0,1,2)

        # Set the range, value and tick interval of the slider
        self.spin_box.setRange(self.symbol_min_qty,self.max_qty)
        self.spin_box.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.spin_box.setPrefix("Quantity: ")
        self.spin_box.valueChanged.connect(self.update_spin_box)

        #THIRD INNER ROW --------------------------------------------------------------------------------------------
        self.value_info_label = QLabel("Value")
        self.value_info_price = QLabel("--")

        self.cost_info_label = QLabel("Cost")
        self.cost_info_price = QLabel("--")

        self.second_row_right_side_first_row_grid_layout.addWidget(self.value_info_label,4,0)
        self.second_row_right_side_first_row_grid_layout.addWidget(self.value_info_price,4,1)
        
        self.second_row_right_side_first_row_grid_layout.addWidget(self.cost_info_label,5,0)
        self.second_row_right_side_first_row_grid_layout.addWidget(self.cost_info_price,5,1)

        #FOURTH INNER ROW --------------------------------------------------------------------------------------------
        self.button_buy_order = QPushButton("Buy")
        self.button_buy_order.clicked.connect(lambda: self.create_order("Buy"))
        self.button_sell_order = QPushButton("Sell")
        self.button_sell_order.clicked.connect(lambda: self.create_order("Sell"))

        self.second_row_right_side_first_row_grid_layout.addWidget(self.button_buy_order,6,0)
        self.second_row_right_side_first_row_grid_layout.addWidget(self.button_sell_order,6,1)

        #FIFTH INNER ROW ---------------------------------------------------------------------------------------------
        self.button_start_bot = QPushButton("Start Bot")
        self.button_start_bot.setCheckable(True)

        self.second_row_right_side_first_row_grid_layout.addWidget(self.button_start_bot,8,0,1,2)
        self.second_row_right_side_layout.addWidget(self.second_row_right_side_first_row_grid_widget)

        #RIGHT SIDE Row #2 --------------------------------------------------------------------------------------------
        self.second_row_right_side_second_row_grid_widget = QWidget()
        self.second_row_right_side_second_row_grid_layout = QGridLayout(self.second_row_right_side_second_row_grid_widget)

        #FIRST INNER ROW ----------------------------------------------------------------------------------------------                
        self.trading_account_label = QLabel("Trading Balance")
        self.second_row_right_side_second_row_grid_layout.addWidget(self.trading_account_label,0,0,1,2)

        #Second INNER ROW ----------------------------------------------------------------------------------------------    
        self.margin_balance_label = QLabel("Margin Balance")
        self.margin_balance_label_number = QLabel("100")
        self.second_row_right_side_second_row_grid_layout.addWidget(self.margin_balance_label,1,0)
        self.second_row_right_side_second_row_grid_layout.addWidget(self.margin_balance_label_number,1,1)

        #Third INNER ROW ----------------------------------------------------------------------------------------------
        self.available_balance_label = QLabel("Available Balance")
        self.available_balance_label_number = QLabel("100")
        self.second_row_right_side_second_row_grid_layout.addWidget(self.available_balance_label,2,0)
        self.second_row_right_side_second_row_grid_layout.addWidget(self.available_balance_label_number,2,1)

        self.second_row_right_side_layout.addWidget(self.second_row_right_side_second_row_grid_widget)

        self.gridLayout_main.addWidget(self.second_row_right_side_grid_widget,1, 1)

        # #Section #3 - Row #3 - Trades info
        self.third_row_widget = QWidget()
        self.third_row_layout = QVBoxLayout(self.third_row_widget)

        # #First Inner Row
        self.third_row_first_inner_row_widget = QWidget()
        self.third_row_first_inner_row_layout = QHBoxLayout(self.third_row_first_inner_row_widget)

        self.third_row_first_inner_row_trade_label = QLabel("Trades")

        self.third_row_first_inner_row_active_positions_button = QPushButton("Positions")
        self.third_row_first_inner_row_active_positions_button.setCheckable(True)
        self.third_row_first_inner_row_active_positions_button.setChecked(True)
        
        self.third_row_first_inner_row_pnl_button = QPushButton("PnL")
        self.third_row_first_inner_row_pnl_button.setCheckable(True)
        self.third_row_first_inner_row_pnl_button.setChecked(False)

        self.third_row_first_inner_row_current_orders_button = QPushButton("Current Orders")
        self.third_row_first_inner_row_current_orders_button.setCheckable(True)
        self.third_row_first_inner_row_current_orders_button.setChecked(False)

        self.third_row_first_inner_row_order_history_button = QPushButton("Order History")
        self.third_row_first_inner_row_order_history_button.setCheckable(True)
        self.third_row_first_inner_row_order_history_button.setChecked(False)

        self.third_row_first_inner_row_trade_history_button = QPushButton("Trade History")
        self.third_row_first_inner_row_trade_history_button.setCheckable(True)
        self.third_row_first_inner_row_trade_history_button.setChecked(False)

        self.third_row_first_inner_row_layout.addWidget(self.third_row_first_inner_row_trade_label)
        self.third_row_first_inner_row_layout.addWidget(self.third_row_first_inner_row_active_positions_button)
        self.third_row_first_inner_row_layout.addWidget(self.third_row_first_inner_row_pnl_button)
        self.third_row_first_inner_row_layout.addWidget(self.third_row_first_inner_row_current_orders_button)
        self.third_row_first_inner_row_layout.addWidget(self.third_row_first_inner_row_order_history_button)
        self.third_row_first_inner_row_layout.addWidget(self.third_row_first_inner_row_trade_history_button)

        self.third_row_layout.addWidget(self.third_row_first_inner_row_widget)

        # Second Inner Row
        self.third_row_second_inner_row_widget = QWidget()
        self.third_row_second_inner_row_layout = QHBoxLayout(self.third_row_second_inner_row_widget)

        self.third_row_second_inner_row_contracts_label = QLabel("Contracts")
        self.third_row_second_inner_row_quantity_label = QLabel("Qty")
        self.third_row_second_inner_row_value_label = QLabel("Trade Value")
        self.third_row_second_inner_row_entry_price_label = QLabel("Entry Price")
        self.third_row_second_inner_row_exit_price_label = QLabel("Exit Price")
        self.third_row_second_inner_row_market_price_label = QLabel("Mark Price")
        self.third_row_second_inner_row_order_price_label = QLabel("Order Price")
        self.third_row_second_inner_row_liquidation_price_label = QLabel("Liq. Price")
        self.third_row_second_inner_row_unrialized_pnl_label = QLabel("Unrealized P&L")
        self.third_row_second_inner_row_realized_pnl_label = QLabel("Realized P&L")
        self.third_row_second_inner_row_take_profit_stop_loss_label = QLabel("TP/SL")
        self.third_row_second_inner_row_close_label = QLabel("Close")
        self.third_row_second_inner_row_trade_type = QLabel('Trade Type')
        self.third_row_second_inner_row_order_type = QLabel('Order Type')
        self.third_row_second_inner_row_order_filled_total = QLabel('Filled/Total')
        self.third_row_second_inner_row_status = QLabel('Status')
        self.third_row_second_inner_row_order_time = QLabel('Order Time')
        self.third_row_second_inner_row_closed_pnl = QLabel('Closed P&L') 
        self.third_row_second_inner_row_oppening_fee = QLabel('Oppening Fee')
        self.third_row_second_inner_row_closing_fee = QLabel('Closing Fee')
        self.third_row_second_inner_row_total_fee = QLabel('Total Fee')

        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_contracts_label)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_trade_type)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_quantity_label)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_value_label)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_entry_price_label)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_market_price_label)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_liquidation_price_label)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_unrialized_pnl_label)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_take_profit_stop_loss_label)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_order_time)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_close_label)

        self.third_row_layout.addWidget(self.third_row_second_inner_row_widget)

        # Create a scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        # Create a container widget to hold the dynamic layouts
        self.scroll_area_widget = QWidget()
        self.container_layout = QVBoxLayout(self.scroll_area_widget)

        # Add the container widget to the scroll area
        self.scroll_area.setWidget(self.scroll_area_widget)
        # Add the scroll area to the main layout
        self.third_row_layout.addWidget(self.scroll_area)

        self.gridLayout_main.addWidget(self.third_row_widget,2,0,1,2)

    def create_graph_widget(self):
        pass

    def open_settings_window(self):
        # Action when "Settings" is selected
        settings_window = SettingsWindow(self.database,self.user_id,self.central_widget)
        settings_window.show()
        settings_window.emitter_update_data.connect(self.update_data)

    def open_trade_settings_window(self):
        trade_settings = TradingSettingsWindow(self.leverage_main,self.leverage_secondary,self.max_leverage,self.central_widget)
        trade_settings.show()
        trade_settings.emitter_confirm_button_clicked.connect(self.update_trading_settings)


    def update_trading_settings(self,data):
        print("Before: Main Leverage:", self.leverage_main, " Secondary Leverage:", self.leverage_secondary)
        if data['leverage_secondary'] == None and self.leverage_secondary == None:
            data['swap_to_original'] = False
            data['swap_to_hedge'] = False
            
            # print(data['leverage_main'], " vs ", self.leverage_main, " - ", data['leverage_main'] == self.leverage_main)
            if int(data['leverage_main']) != int(self.leverage_main):
                self.leverage_main = data['leverage_main']
                data['leverage_secondary'] = self.leverage_main
                self.emitter_update_trading_settings.emit(data)

        elif data['leverage_secondary'] != None and self.leverage_secondary != None:
            data['swap_to_original'] = False
            data['swap_to_hedge'] = False

            # print(data['leverage_secondary'], " vs ", self.leverage_secondary, " - ", data['leverage_secondary'] == self.leverage_secondary)
            # print(data['leverage_main'], " vs ", self.leverage_main, " - ", data['leverage_main'] == self.leverage_main)
            if int(data['leverage_secondary']) != int(self.leverage_secondary) or int(data['leverage_main']) != int(self.leverage_main):
                self.leverage_main = data['leverage_main']
                self.leverage_secondary = data['leverage_secondary']
                self.emitter_update_trading_settings.emit(data)

        elif data['leverage_secondary'] == None and self.leverage_secondary != None:
            data['swap_to_original'] = True
            data['swap_to_hedge'] = False
            self.posIdxInfo = 0
            self.leverage_secondary = None
            self.leverage_main = data['leverage_main']
            data['leverage_secondary'] = self.leverage_main
            self.emitter_update_trading_settings.emit(data)
        elif data['leverage_secondary'] != None and self.leverage_secondary == None:
            data['swap_to_original'] = False
            data['swap_to_hedge'] = True
            self.posIdxInfo = 1
            self.leverage_secondary = data['leverage_secondary']
            self.leverage_main = data['leverage_main']
            self.emitter_update_trading_settings.emit(data)

        

    def changeCoin(self, coin_name):
        pass



    def update_data(self,user_data):
        self.emitter_update_data.emit(user_data)

    def logout(self):
        self.user_data = None
        self.user_id = None
        self.emitter_logout.emit("")

    def limit_button_clicked(self):
        self.button_limit_order.setChecked(True)
        if self.button_limit_order.isChecked():
            # Handle the limit button being selected
            self.button_market_order.setChecked(False)

    def market_button_clicked(self):
        self.button_market_order.setChecked(True)
        if self.button_market_order.isChecked():
            # Handle the market button being selected
            self.button_limit_order.setChecked(False)

    def handle_pnl_labels(self,data):
        pass

    def pnl_button_clicked(self,data):
        # print(data)
        self.clear_scroll_area()
        self.is_position_layout_created = False
        self.third_row_first_inner_row_active_positions_button.setChecked(False)
        self.third_row_first_inner_row_pnl_button.setChecked(True)
        self.third_row_first_inner_row_current_orders_button.setChecked(False)
        self.third_row_first_inner_row_order_history_button.setChecked(False)
        self.third_row_first_inner_row_trade_history_button.setChecked(False)

        self.clear_second_inner_row_labels()

        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_contracts_label)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_quantity_label)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_entry_price_label)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_exit_price_label)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_trade_type)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_closed_pnl)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_oppening_fee)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_closing_fee)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_total_fee)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_order_time)
        
        self.handle_pnl_labels(data)

    def handle_current_orders_labels(self,data):
        pass

    def current_orders_button_clicked(self,data):
        self.clear_scroll_area()
        self.is_position_layout_created = False
        self.third_row_first_inner_row_active_positions_button.setChecked(False)
        self.third_row_first_inner_row_pnl_button.setChecked(False)
        self.third_row_first_inner_row_current_orders_button.setChecked(True)
        self.third_row_first_inner_row_order_history_button.setChecked(False)
        self.third_row_first_inner_row_trade_history_button.setChecked(False)

        self.clear_second_inner_row_labels()

        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_contracts_label)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_quantity_label)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_order_price_label)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_order_filled_total)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_take_profit_stop_loss_label)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_trade_type)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_order_type)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_status)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_order_time)

        self.handle_current_orders_labels(data)


    def handle_order_history_labels(self,data):
        pass

    def order_history_button_clicked(self,data):
        self.clear_scroll_area()
        self.is_position_layout_created = False
        self.third_row_first_inner_row_active_positions_button.setChecked(False)
        self.third_row_first_inner_row_pnl_button.setChecked(False)
        self.third_row_first_inner_row_current_orders_button.setChecked(False)
        self.third_row_first_inner_row_order_history_button.setChecked(True)
        self.third_row_first_inner_row_trade_history_button.setChecked(False)
    
        self.clear_second_inner_row_labels()

        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_contracts_label)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_quantity_label)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_entry_price_label)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_value_label)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_trade_type)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_order_type)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_status)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_order_time)

        self.handle_order_history_labels(data)

    def handle_trade_history_labels(self,data):
        pass

    def trade_history_button_clicked(self,data):
        self.clear_scroll_area()
        self.is_position_layout_created = False
        self.third_row_first_inner_row_active_positions_button.setChecked(False)
        self.third_row_first_inner_row_pnl_button.setChecked(False)
        self.third_row_first_inner_row_current_orders_button.setChecked(False)
        self.third_row_first_inner_row_order_history_button.setChecked(False)
        self.third_row_first_inner_row_trade_history_button.setChecked(True)

        self.clear_second_inner_row_labels()

        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_contracts_label)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_quantity_label)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_entry_price_label)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_value_label)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_trade_type)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_total_fee)
        self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_order_time)

        self.handle_trade_history_labels(data)

    def timeframe_button_clicked(self,new_interval):
        self.one_minute_timeframe_button.setChecked(False)
        self.five_minute_timeframe_button.setChecked(False)
        self.fiveteen_minutes_timeframe_button.setChecked(False)
        self.thiry_minutes_timeframe_button.setChecked(False)
        self.one_hour_timeframe_button.setChecked(False)
        self.four_hours_timeframe_button.setChecked(False)
        self.one_day_timeframe_button.setChecked(False)
        self.one_week_timeframe_button.setChecked(False)
        self.one_month_timeframe_button.setChecked(False)
        
        if new_interval == "1m":
            self.one_minute_timeframe_button.setChecked(True)
        elif new_interval == "5m":
            self.five_minute_timeframe_button.setChecked(True)
        elif new_interval == "15m":
            self.fiveteen_minutes_timeframe_button.setChecked(True)
        elif new_interval == "30m":
            self.thiry_minutes_timeframe_button.setChecked(True)
        elif new_interval == "1h":
            self.one_hour_timeframe_button.setChecked(True)
        elif new_interval == "4h":
            self.four_hours_timeframe_button.setChecked(True)
        elif new_interval == "1D":
            self.one_day_timeframe_button.setChecked(True)
        elif new_interval == "1W":
            self.one_week_timeframe_button.setChecked(True)
        elif new_interval == "1M":
            self.one_month_timeframe_button.setChecked(True)

        self.change_graph_interval(new_interval)

    def change_graph_interval(self,new_interval):
        pass
    
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
    
    def create_order(self,side):
        entry_type = False
        if self.button_market_order.isChecked():
            entry_type = "Market"
        else:
            entry_type = "Limit"

        if self.posIdxInfo == 0:
            data = {"entry_type" : entry_type, "quantity": self.spin_box.value(), "side": side, "posIdx": 0}
        elif side == "Buy":
            data = {"entry_type" : entry_type, "quantity": self.spin_box.value(), "side":side, "posIdx": 1}
        else:
            data = {"entry_type" : entry_type, "quantity": self.spin_box.value(), "side": side, "posIdx": 2}
        self.emitter_buy_order.emit(data)

    
    def remove_widget_safely(layout, widget):
        # Check if the widget is in the layout
        index = layout.indexOf(widget)
        
        if index != -1:
            # Widget is in the layout, remove it
            layout.removeWidget(widget)
            widget.setParent(None)

    def add_widget_safely(layout, widget):
        # Check if the widget is not in the layout
        if layout.indexOf(widget) == -1:
            # Widget is not in the layout, add it
            layout.addWidget(widget)

    def clear_second_inner_row_labels(self):
        widgets_to_remove = []

        # Add widgets to the list
        for i in range(self.third_row_second_inner_row_layout.count()):
            item = self.third_row_second_inner_row_layout.itemAt(i)
            widget = item.widget()
            widgets_to_remove.append(widget)

        # Remove widgets from the layout
        for widget in widgets_to_remove:
            self.third_row_second_inner_row_layout.removeWidget(widget)
            widget.setParent(None)

        self.third_row_second_inner_row_layout.update()


    def clear_scroll_area(self):
        self.active_positions = []
        # Clear existing widgets in the container layout
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Update the container widget and the scroll area
        self.scroll_area_widget.update()
        self.scroll_area.update()

    def handle_position_data(self,data):
        pass

    def close_button_clicked(self,data):
        # print(data)
        self.emitter_close_position.emit(data)

    def update_position_data(self,data):
        # print(data)
        positions_data = self.handle_position_data(data)
        if(self.third_row_first_inner_row_active_positions_button.isChecked()):
            if self.is_position_layout_created is False:
                self.clear_scroll_area()
                self.is_position_layout_created = True
                self.third_row_first_inner_row_active_positions_button.setChecked(True)
                self.third_row_first_inner_row_pnl_button.setChecked(False)
                self.third_row_first_inner_row_current_orders_button.setChecked(False)
                self.third_row_first_inner_row_order_history_button.setChecked(False)
                self.third_row_first_inner_row_trade_history_button.setChecked(False)

                self.clear_second_inner_row_labels()

                self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_contracts_label)
                self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_trade_type)
                self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_quantity_label)
                self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_value_label)
                self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_entry_price_label)
                self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_market_price_label)
                self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_liquidation_price_label)
                self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_unrialized_pnl_label)
                self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_take_profit_stop_loss_label)
                self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_order_time)
                self.third_row_second_inner_row_layout.addWidget(self.third_row_second_inner_row_close_label)


            active_symbols = []
            for current_position in positions_data:
                position_side = current_position['side']
                if(position_side != ''):
                    currentTrade = {"symbol": current_position['symbol'], "posIdx": current_position['positionIdx']}
                    is_position_found = False
                    active_symbols.append(currentTrade)
                    if len(self.active_positions) > 0:
                        for position in self.active_positions:
                            if current_position['symbol'] == position.symbol and current_position['positionIdx'] == position.position_index:
                                is_position_found = True
                                position.update_data(current_position)
                                break
                        
                    if is_position_found is False:
                        self.active_positions.append(ActivePositionWidget(current_position))
                        self.active_positions[len(self.active_positions) - 1].emitter_close_position.connect(self.close_button_clicked)
                        self.container_layout.addWidget(self.active_positions[len(self.active_positions) - 1])

            for position in self.active_positions[:]: 
                is_position_found = False
                for trade_data in active_symbols:
                    if position.symbol == trade_data["symbol"] and position.position_index == trade_data["posIdx"]:
                        is_position_found = True
                        break
                if is_position_found is False:
                    self.container_layout.removeWidget(position)
                    position.deleteLater()
                    self.active_positions.remove(position)
            
            if len(self.active_positions) == 0 and self.third_row_second_inner_row_layout.count() != 0:
                self.clear_scroll_area()
                self.is_position_layout_created = False

    def math_floor_decimal(self,number):
        scaled_number = number * 10 ** self.symbol_decimals
        floored_number = math.floor(scaled_number)
        return floored_number / 10 ** self.symbol_decimals

    def update_spin_box(self, value):
        # self.spin_box.setValue(value)
        if value == 0:
            self.value_info_price.setText("--")
            self.cost_info_price.setText("--")
        else:
            if(self.available_balance_label_number.text() != "Not Connected"):
                value = self.math_floor_decimal(value)

                cost = float(self.available_balance_label_number.text()) * (self.math_floor_decimal(value / self.max_qty))
                self.cost_info_price.setText("{:.4f}".format(cost))
                self.value_info_price.setText("{:.2f}".format(self.last_price * value))


    def update_min_qty(self,minQty):
        self.symbol_min_qty = minQty
        self.spin_box.setRange(0,float(self.max_qty))
        self.symbol_decimals = self.get_decimals_amount(minQty)
        self.spin_box.setDecimals(self.symbol_decimals)
        
    def get_decimals_amount(self,number):
        parts = number.split('.')
        return len(parts[1]) if len(parts) == 2 else None

    def update_max_qty(self, last_price):
        self.last_price = last_price
        balance = float(self.available_balance_label_number.text())        
        # Convert self.leverage to float if it's not already
        leverage = float(self.leverage_main)
        # Convert last_price to float if it's not already
        last_price = float(last_price)

        self.max_qty = (leverage * balance) / last_price
        scaled_number = self.max_qty * 10 ** self.symbol_decimals
        floored_number = math.floor(scaled_number)
        self.max_qty = floored_number / 10 ** self.symbol_decimals
        self.spin_box.setRange(0, float(self.max_qty))

    def percent_button_clicked(self,percent):
        value = self.max_qty * (percent/100)
        scaled_number = value * 10 ** self.symbol_decimals
        floored_number = math.floor(scaled_number)
        self.spin_box.setValue(floored_number / 10 ** self.symbol_decimals)
        self.update_spin_box(value)
    
    def update_leverage_label(self):
        if self.leverage_secondary != None:
            string = str(self.leverage_main) + " " + str(self.leverage_secondary)
            self.leverage_label.setText(string)
        else:
            self.leverage_label.setText(str(self.leverage_main))

    def setup_main_window_positioning(self):
        self.gridLayout_main.setRowStretch(1, 3)
        self.gridLayout_main.setRowStretch(2, 2)
        self.gridLayout_main.setColumnStretch(0, 4)
        self.gridLayout_main.setColumnStretch(1, 1)

        # self.coin_data_layout.setStretch(0,1)
        # self.coin_data_layout.setStretch(1,1)
        # self.coin_data_layout.setStretch(2,5)

        self.third_row_first_inner_row_layout.setStretch(0,1)
        self.third_row_first_inner_row_layout.setStretch(2,3)
        self.third_row_first_inner_row_layout.setStretch(3,3)
        self.third_row_first_inner_row_layout.setStretch(4,3)
        self.third_row_first_inner_row_layout.setStretch(5,3)
        self.third_row_first_inner_row_layout.setStretch(6,3)
        self.third_row_first_inner_row_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # Create a central widget and set the layout
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.gridLayout_main)

    def setup_main_window_css(self):
        self.central_widget.setStyleSheet("background-color: #101014;")
        
        #Seciton #1 - Daily Coin Data + Account Bar
        self.coin_data_widget.setStyleSheet("background-color: #08080a; color: #a8a8a8; font-size: 12px; border: 1px solid #333333; border-radius: 5px; font-family: BinancePlex, Arial;")
        self.account_data_widget.setStyleSheet("background-color: #08080a; color: #a8a8a8; font-size: 12px; border: 1px solid #333333; border-radius: 5px; font-family: BinancePlex, Arial;")
        
        # self.coin_name_label.setStyleSheet("font-size: 20px; font-weight: bold")
        self.chosen_coin_menu_button.setStyleSheet("font-size: 20px; font-weight: bold; padding: 5px")
        self.coin_price_label_number.setStyleSheet("font-size: 20px; text-align: center;")
        self.menu_button.setStyleSheet("font-size: 20px; font-weight: bold")


        self.one_minute_timeframe_button.setStyleSheet("""QPushButton:checked { border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 5px;}""")
        self.five_minute_timeframe_button.setStyleSheet("""QPushButton:checked { border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 5px;}""")
        self.fiveteen_minutes_timeframe_button.setStyleSheet("""QPushButton:checked { border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 5px;}""")
        self.thiry_minutes_timeframe_button.setStyleSheet("""QPushButton:checked { border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 5px;}""")
        self.one_hour_timeframe_button.setStyleSheet("""QPushButton:checked { border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 5px;}""")
        self.four_hours_timeframe_button.setStyleSheet("""QPushButton:checked { border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 5px;}""")
        self.one_day_timeframe_button.setStyleSheet("""QPushButton:checked { border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 5px;}""")
        self.one_week_timeframe_button.setStyleSheet("""QPushButton:checked { border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 5px;}""")
        self.one_month_timeframe_button.setStyleSheet("""QPushButton:checked { border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 5px;}""")
        

        #Section #2 - Candlestick Graph + Trade Options and Wallet Ballance
        self.second_row_left_side_graph_widget.setStyleSheet("background-color: #08080a; border: 1px solid #333333; border-radius: 5px;")
        self.second_row_right_side_grid_widget.setStyleSheet("background-color: #08080a; border: 1px solid #333333; border-radius: 5px; color: #a8a8a8; font-size: 12px; font-family: BinancePlex, Arial; ")
        
        self.trading_account_label.setStyleSheet("color: #a8a8a8; font-size: 20px; font-weight: bold")
        self.trading_account_label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        
        self.button_limit_order.setStyleSheet("""
                                      QPushButton { background-color: #101014; border: 2px solid #a8a8a8; color: #a8a8a8; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 10px;} 
                                      QPushButton:pressed { background-color: #101014; border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 10px;} 
                                      QPushButton:checked { background-color: #101014; border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 10px;}
                                      """)
        self.button_market_order.setStyleSheet("""
                                      QPushButton { background-color: #101014; border: 2px solid #a8a8a8; color: #a8a8a8; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 10px;} 
                                      QPushButton:pressed { background-color: #101014; border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 10px;} 
                                      QPushButton:checked { background-color: #101014; border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 10px;}
                                      """)

        self.button_buy_order.setStyleSheet("QPushButton { background-color: #4CAF50; border: none; padding: 10px 15x;  border-radius: 10px; color: white; text-align: center; text-decoration: none; font-size: 16px; }")
        self.button_sell_order.setStyleSheet("QPushButton { background-color: #f50000; border-radius: 10px; padding: 10px 15x;  border-radius: 10px; color: white; font-family: BinancePlex, Arial; font-size: 16px} ")
        self.button_start_bot.setStyleSheet("""
                                            QPushButton { background-color: #101014; border: 2px solid #a8a8a8; color: #a8a8a8; padding: 10px 15x;  border-radius: 10px; font-family: BinancePlex, Arial; text-align: center; text-decoration: none; font-size: 16px; }
                                            QPushButton:checked { background-color: #101014; border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 10px;}
                                            """)

        #Section #3 - Menu - Live Position Data, P&L History, Order History and Trade History
        self.third_row_second_inner_row_widget.setStyleSheet("color: #a8a8a8; font-family: BinancePlex, Arial;  text-decoration: none; font-size: 12px;")
        self.third_row_first_inner_row_trade_label.setStyleSheet("color:#ffa200; font-family: BinancePlex, Arial; text-align: center; text-decoration: none; font-size: 12px;")
        self.third_row_first_inner_row_trade_label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

        # self.scroll_area_widget.setStyleSheet("color: #a8a8a8; font-family: BinancePlex, Arial; padding: 1px 1x; text-decoration: none; font-size: 12px;")
        self.third_row_widget.setStyleSheet("background-color: #08080a; border: 1px solid #333333; border-radius: 5px;")
        self.scroll_area_widget.setStyleSheet("color: #a8a8a8; font-family: BinancePlex, Arial; padding: 1px 1x; text-decoration: none; font-size: 12px; border: 1px solid #a8a8a8;")
        self.scroll_area.setStyleSheet("QScrollArea { border: 1px solid #a8a8a8; padding: 1px 1x; }")
        self.container_layout.setAlignment(Qt.AlignTop)


        self.third_row_first_inner_row_active_positions_button.setStyleSheet("""
                                            QPushButton { padding: 3px; width: 100%; border: 2px solid #a8a8a8;color: #a8a8a8;  border-radius: 5px; font-family: BinancePlex, Arial; text-align: center; text-decoration: none; font-size: 12px; }
                                            QPushButton:checked { border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 5px;}
                                            """)
        self.third_row_first_inner_row_pnl_button.setStyleSheet("""
                                            QPushButton { padding: 3px; width: 60%; border: 2px solid #a8a8a8;  color: #a8a8a8; border-radius: 5px; font-family: BinancePlex, Arial; text-align: center; text-decoration: none; font-size: 12px; }
                                            QPushButton:checked {  border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 5px;}
                                            """)
        self.third_row_first_inner_row_current_orders_button.setStyleSheet("""
                                            QPushButton { padding: 3px; width: 100%; border: 2px solid #a8a8a8;  color: #a8a8a8; border-radius: 5px; font-family: BinancePlex, Arial; text-align: center; text-decoration: none; font-size: 12px; }
                                            QPushButton:checked {  border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 5px;}
                                            """)
        self.third_row_first_inner_row_order_history_button.setStyleSheet("""
                                            QPushButton { padding: 3px; width: 100%; border: 2px solid #a8a8a8;  color: #a8a8a8;  border-radius: 5px; font-family: BinancePlex, Arial; text-align: center; text-decoration: none; font-size: 12px; }
                                            QPushButton:checked {  border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 5px;}
                                            """)
        self.third_row_first_inner_row_trade_history_button.setStyleSheet("""
                                            QPushButton { padding: 3px; width: 100%; border: 2px solid #a8a8a8; color: #a8a8a8; border-radius: 5px; font-family: BinancePlex, Arial; text-align: center; text-decoration: none; font-size: 12px; }
                                            QPushButton:checked {  border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 5px;}
                                            """)


        # Set the font and color of the spin box
        self.spin_box.setFont(QtGui.QFont("BinancePlex, Arial", 14))
        self.spin_box.setStyleSheet("QSpinBox { color: #ffa200; }")

        self.second_row_left_side_graph_widget.setStyleSheet("background-color: #101014")