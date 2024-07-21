from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QThread, pyqtSignal
from stable_baselines3 import PPO
from user_interface.login_interface import LoginInterface
from user_interface.bybit_interface import BybitUserInterface
from user_interface.mexc_interface import MexcUserInterface
from models.LiveTradingEnv import LiveTradingEnv
from exchange_APIs.bybit_exchange import BybitExchange
from exchange_APIs.mexc_exchange import MexcExchange
from data_acquisition.bybit_history_data import BybitHistoryData
from database import DataBase
import numpy as np
import pandas as pd
import asyncio
import sys

class TradingThread(QThread):
    emitter_model_results = pyqtSignal(object)  # Signal to send data back to the main thread

    def __init__(self, model_path, live_env):
        super().__init__()
        self.model = PPO.load(model_path)
        self.live_env = live_env
        self.current_state = self.live_env.reset()
        self.running = False

    def run(self,data):
        if('data' in data and self.running is True):
                current_data = []
                current_data.append(int(data['data'][0]['start']))
                current_data.append(float(data['data'][0]['open']))
                current_data.append(float(data['data'][0]['high']))
                current_data.append(float(data['data'][0]['low']))
                current_data.append(float(data['data'][0]['close']))
                current_data.append(float(data['data'][0]['volume']))
                current_data.append(float(data['data'][0]['turnover']))
                self.live_env.df.loc[len(self.live_env.df)] = current_data              
                self.live_env.current_step = len(self.live_env.df) - 1
                current_data_state = self.live_env.df.iloc[self.live_env.current_step].values.astype(np.float32)
                action, _states = self.model.predict(current_data_state)
                new_state, reward, done, info = self.live_env.step(action)

                if(data['data'][0]['confirm'] is False):
                    self.live_env.df = self.live_env.df.drop(self.live_env.df.index[-1])
                else:
                    print("Action Was: ",action)
                    self.live_env.current_step = len(self.live_env.df) - 1
                    is_gap, gap = self.live_env.if_current_candle_in_gap()

                    if(is_gap != 0):
                        if is_gap == 1:
                            print('Long Gap Removed: ',gap)
                            self.live_env.long_gaps.remove(gap)
                        else:
                            print('Short Gap Removed:',gap)
                            self.live_env.short_gaps.remove(gap)
                    
                    print('There are :',len(self.live_env.long_gaps), ' Long Gaps')
                    if(len(self.live_env.long_gaps) > 0 ):
                        closest_long_gap = self.live_env.long_gaps[len(self.live_env.long_gaps) - 1]
                        print('Closest Long Gap is:', closest_long_gap)

                    print('There are :',len(self.live_env.short_gaps), ' Short Gaps')
                    if(len(self.live_env.short_gaps) > 0 ):
                        closest_short_gap = self.live_env.short_gaps[len(self.live_env.short_gaps) - 1]
                        print('Closest Short Gap is:', closest_short_gap)

                    self.emitter_model_results.emit((new_state, reward, done, info))

                if done:
                    self.live_env.reset()

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

class MainWindow(QMainWindow):
    data_received_signal = pyqtSignal(object)
    graph_df = None
    bot_symbol = None
    graph_interval = None

    def __init__(self,symbol="BTCUSDT", interval="1"):
        super().__init__()
        self.graph_symbol = symbol
        self.graph_interval = interval

        # Set window title and dimensions
        self.setWindowTitle('Trading Bot')
        self.setGeometry(500, 200, 1000, 800)

        #Connect to the Database
        self.database = DataBase()

        #Load the main interface(Login Window)
        self.user_interface = LoginInterface(self.database)
        
        self.setCentralWidget(self.user_interface.central_widget_register_window)
        self.user_interface.emitter_open_main_window.connect(self.run_main)

    def run_main(self,user_data):
        self.user_data = user_data
        self.stream_thread = QThread()
        self.bot_symbol = user_data['account_settings']['bot_settings']['trading_contract']
        self.bot_interval = user_data['account_settings']['bot_settings']['used_timeframe']
        self.graph_symbol = user_data['account_settings']['bot_settings']['trading_contract']
        self.account_risk = user_data['account_settings']['bot_settings']['account_risk']
        self.is_account_demo = user_data['account_settings']['is_account_demo']
        if self.is_account_demo is False:
            self.is_bybit_used = user_data['account_settings']['exchange_settings']['bybit_button_clicked']
            self.exchange_bot_data = None
            self.exchange_graph_data = None
            self.wallet_balance = 0
            if self.is_bybit_used:
                self.API_KEY = user_data['account_settings']['exchange_settings']['bybit_api_key']
                self.SECRET_KEY = user_data['account_settings']['exchange_settings']['bybit_secret_key']
                self.exchange_bot_data = BybitExchange(self.API_KEY,self.SECRET_KEY)
                self.exchange_graph_data = BybitExchange()
                self.instrument_info = asyncio.run(self.exchange_graph_data.instrument_info("linear",self.graph_symbol))
                self.user_interface = BybitUserInterface(self.database,self.user_data,self.graph_symbol,self.graph_interval)
                self.set_interface_user_settings()         
            else:
                self.API_KEY = user_data['account_settings']['exchange_settings']['mexc_api_key']
                self.SECRET_KEY = user_data['account_settings']['exchange_settings']['mexc_secret_key']
                self.exchange_bot_data = MexcExchange(self.API_KEY,self.SECRET_KEY)
                self.exchange_graph_data = MexcExchange()
                if self.API_KEY != "" and self.SECRET_KEY != "": 
                    self.wallet_balance = self.exchange_bot_data.get_account_assets() #TODO 
                    self.wallet_balance = float(self.wallet_balance['result']['list'][0]['totalEquity'])#TODO
                self.user_interface = MexcUserInterface(self.database,self.user_data,self.graph_symbol,self.graph_interval)

            self.risk_to_reward_string = self.user_data['account_settings']['bot_settings']['risk_to_reward']
            firstNum, secondNum = map(float, self.risk_to_reward_string.split(":"))
            risk_to_reward = secondNum / firstNum
            self.exchange_bot_data.moveToThread(self.stream_thread)
            self.stream_thread.start()
            data = BybitHistoryData(category="linear",symbol=self.bot_symbol, interval=self.bot_interval)
            self.bot_df = pd.DataFrame(data.klines, columns=["open_time", "open_price", "high_price", "low_price", "close_price", "volume", "turnover"])
            self.graph_df = self.user_interface.df
            self.live_env = LiveTradingEnv(self.bot_df,self.wallet_balance,risk_to_reward, self.account_risk)
            self.trading_thread = TradingThread("models\\models\\reinforcement_learning_all_data.zip", self.live_env)

            self.setCentralWidget(self.user_interface.central_widget)
            self.set_connections()
            print("Successfully Logged In")
        else:
            self.API_KEY = ""
            self.SECRET_KEY = ""
            self.wallet_balance = 1000
            self.risk_to_reward_string = self.user_data['account_settings']['bot_settings']['risk_to_reward']
            firstNum, secondNum = map(float, self.risk_to_reward_string.split(":"))
            risk_to_reward = secondNum / firstNum
            self.user_interface = BybitUserInterface(self.database,self.user_data,self.graph_symbol,self.graph_interval)
            self.exchange_graph_data = BybitExchange()
            self.graph_df = self.user_interface.df
            self.live_env = LiveTradingEnv(self.graph_df,self.wallet_balance,risk_to_reward, 0.02)
            self.trading_thread = TradingThread("models\\models\\reinforcement_learning_all_data.zip", self.live_env)
            self.setCentralWidget(self.user_interface.central_widget)
            self.set_connections()

    def create_order(self,data):
        result = asyncio.run(self.exchange_bot_data.create_order(symbol=self.graph_symbol,type=data['side'],entry_type=data['entry_type'],quantity=data['quantity'],positionIdx=data['posIdx']))
        if result['retMsg'] != "OK" and result['retMsg'] != "success" and result['retMsg'] != "SUCCESS" and result['retMsg'] != "":
            print(result)

    def update_trading_settings(self,data):
        if data['swap_to_original']:
            switch_mode_result = asyncio.run(self.exchange_bot_data.switch_mode(self.graph_symbol,0))
            if switch_mode_result['retMsg'] != "OK" and switch_mode_result['retMsg'] != "success" and switch_mode_result['retMsg'] != "SUCCESS" and switch_mode_result['retMsg'] != "":
                print(switch_mode_result)
        elif data['swap_to_hedge']:
            switch_mode_result = asyncio.run(self.exchange_bot_data.switch_mode(self.graph_symbol,3))
            if switch_mode_result['retMsg'] != "OK" and switch_mode_result['retMsg'] != "success" and switch_mode_result['retMsg'] != "SUCCESS" and switch_mode_result['retMsg'] != "":
                print(switch_mode_result)
        
        result = asyncio.run(self.exchange_bot_data.set_leverage(self.graph_symbol, data['leverage_main'], data['leverage_secondary']))
        if result['retMsg'] != "OK" and result['retMsg'] != "success" and result['retMsg'] != "SUCCESS" and result['retMsg'] != "":
            print(result)
            
        self.user_interface.update_leverage_label()

    def set_connections(self):
        self.exchange_graph_data.emitter_kline_data.connect(self.user_interface.update_chart)
        self.exchange_graph_data.emitter_ticker_data.connect(self.user_interface.update_ticker_labels)
        self.user_interface.emitter_update_data.connect(self.update_settings)
        self.user_interface.emitter_update_trading_settings.connect(self.update_trading_settings)
        self.user_interface.emitter_buy_order.connect(self.create_order)
        self.user_interface.emitter_change_coin_graph.connect(self.change_graph_symbol)
        self.user_interface.emitter_change_interval_graph.connect(self.change_graph_interval)
        self.user_interface.emitter_close_position.connect(self.close_position)
        self.user_interface.emitter_logout.connect(self.logout)

        if self.API_KEY != "" and self.SECRET_KEY != "":
            self.exchange_bot_data.emitter_kline_data.connect(self.get_position_info)
            self.trading_thread.emitter_model_results.connect(self.use_model_results) 
            self.exchange_bot_data.emitter_kline_data.connect(self.trading_thread.run)

            self.set_app_connections()
            self.set_interface_connections()

            self.exchange_bot_data.subscrbe_to_kline(self.bot_symbol,self.bot_interval)
            self.exchange_bot_data.subscribe_to_wallet()

        self.exchange_graph_data.subscrbe_to_kline(self.graph_symbol,self.graph_interval)
        self.exchange_graph_data.subscribe_to_ticker(self.graph_symbol)

    def close_position(self,data):
        asyncio.run(self.exchange_bot_data.close_trade(data['symbol'], data['side'], 'Market',data['size'],data['position_index']))

    def change_graph_symbol(self,symbol):
        self.graph_symbol = symbol

        self.exchange_graph_data.unsubscribe_from_kline()
        self.exchange_graph_data.unsubscribe_from_ticker()

        self.exchange_graph_data.subscrbe_to_kline(self.graph_symbol,self.graph_interval)
        self.exchange_graph_data.subscribe_to_ticker(self.graph_symbol)

        self.instrument_info = asyncio.run(self.exchange_graph_data.instrument_info("linear",self.graph_symbol))
        get_graph_coin_info = asyncio.run(self.exchange_bot_data.get_position_info(symbol=self.graph_symbol))
        self.user_interface.update_min_qty(self.instrument_info['result']['list'][0]['lotSizeFilter']['minOrderQty'])
        
        self.graph_leverage = get_graph_coin_info['result']['list'][0]['leverage']
        self.user_interface.posIdxInfo = get_graph_coin_info['result']['list'][0]['positionIdx']
        
        if self.user_interface.posIdxInfo == 0:
            self.user_interface.leverage_main = self.graph_leverage
            self.user_interface.leverage_secondary = None
        elif self.user_interface.posIdxInfo == 1:
            self.user_interface.leverage_main = self.graph_leverage
            self.user_interface.leverage_secondary = get_graph_coin_info['result']['list'][1]['leverage']
        else:
            self.user_interface.leverage_secondary = self.graph_leverage
            self.user_interface.leverage_main = get_graph_coin_info['result']['list'][1]['leverage']
        self.user_interface.update_leverage_label()

    def change_graph_interval(self,interval):
        self.graph_interval = interval

        self.exchange_graph_data.unsubscribe_from_kline()
        self.exchange_graph_data.subscrbe_to_kline(self.graph_symbol,self.graph_interval)

    def set_interface_connections(self):
        self.user_interface.button_start_bot.clicked.connect(self.toggle_trading)    
        self.user_interface.third_row_first_inner_row_order_history_button.clicked.connect(lambda: asyncio.run(self.exchange_bot_data.get_order_history()))
        self.user_interface.third_row_first_inner_row_trade_history_button.clicked.connect(lambda: asyncio.run(self.exchange_bot_data.get_trade_history()))
        self.user_interface.third_row_first_inner_row_current_orders_button.clicked.connect(lambda: asyncio.run(self.exchange_bot_data.get_open_orders()))
        self.user_interface.third_row_first_inner_row_pnl_button.clicked.connect(lambda: asyncio.run(self.exchange_bot_data.get_pnl_closed()))

    def clear_interface_connections(self):
        self.user_interface.one_minute_timeframe_button.clicked.disconnect()
        self.user_interface.five_minute_timeframe_button.clicked.disconnect()
        self.user_interface.fiveteen_minutes_timeframe_button.clicked.disconnect()
        self.user_interface.thiry_minutes_timeframe_button.clicked.disconnect()
        self.user_interface.one_hour_timeframe_button.clicked.disconnect()
        self.user_interface.four_hours_timeframe_button.clicked.disconnect()
        self.user_interface.one_day_timeframe_button.clicked.disconnect()
        self.user_interface.one_week_timeframe_button.clicked.disconnect()
        self.user_interface.one_month_timeframe_button.clicked.disconnect()

    def set_app_connections(self):
        self.exchange_bot_data.emitter_wallet_data.connect(self.user_interface.update_wallet_data)
        self.exchange_bot_data.emitter_position_data.connect(self.user_interface.update_position_data)
        self.exchange_bot_data.emitter_order_history_data.connect(self.user_interface.order_history_button_clicked)
        self.exchange_bot_data.emitter_trade_history_data.connect(self.user_interface.trade_history_button_clicked)
        self.exchange_bot_data.emitter_open_orders_data.connect(self.user_interface.current_orders_button_clicked)
        self.exchange_bot_data.emitter_pnl_closed_data.connect(self.user_interface.pnl_button_clicked)
        self.exchange_bot_data.emitter_wallet_balance_data.connect(self.user_interface.set_account_balance)
        asyncio.run(self.exchange_bot_data.get_wallet_balance())

    def clear_app_connections(self):
        self.exchange_bot_data.emitter_wallet_data.disconnect(self.user_interface.update_wallet_data)
        self.exchange_bot_data.emitter_position_data.disconnect(self.user_interface.update_position_data)
        self.exchange_bot_data.emitter_order_history_data.disconnect(self.user_interface.order_history_button_clicked)
        self.exchange_bot_data.emitter_trade_history_data.disconnect(self.user_interface.trade_history_button_clicked)
        self.exchange_bot_data.emitter_open_orders_data.disconnect(self.user_interface.current_orders_button_clicked)
        self.exchange_bot_data.emitter_pnl_closed_data.disconnect(self.user_interface.pnl_button_clicked)
        self.exchange_bot_data.emitter_wallet_balance_data.disconnect(self.user_interface.set_account_balance)

    def get_position_info(self,data):
        asyncio.run(self.exchange_bot_data.get_positions())

    def logout(self):
            if self.API_KEY != "":
                self.exchange_bot_data.emitter_kline_data.disconnect(self.get_position_info)
                self.exchange_bot_data.emitter_kline_data.disconnect(self.trading_thread.run)
                self.trading_thread.emitter_model_results.disconnect(self.use_model_results) 
                self.clear_app_connections()
                self.user_interface.button_start_bot.clicked.disconnect(self.toggle_trading)
                self.user_interface.third_row_first_inner_row_order_history_button.clicked.disconnect()
                self.user_interface.third_row_first_inner_row_trade_history_button.clicked.disconnect()
                self.user_interface.third_row_first_inner_row_current_orders_button.clicked.disconnect()
                # self.user_interface.third_row_first_inner_row_active_positions_button.clicked.disconnect()
                self.user_interface.third_row_first_inner_row_pnl_button.clicked.disconnect()
                self.exchange_bot_data.unsubscribe_from_kline()

            self.exchange_graph_data.emitter_kline_data.disconnect(self.user_interface.update_chart)
            self.exchange_graph_data.emitter_ticker_data.disconnect(self.user_interface.update_ticker_labels)
            self.user_interface.emitter_update_data.disconnect(self.update_settings)
            self.user_interface.emitter_logout.disconnect(self.logout)
            self.exchange_graph_data.unsubscribe_from_kline()
            self.exchange_graph_data.unsubscribe_from_ticker()
            self.is_bybit_used = None
            self.exchange_bot_data = None
            self.graph_df = None
            self.trading_thread.running = False
            self.live_env = None
            self.trading_thread = None
            self.stream_thread.quit()
            self.stream_thread.wait()
            self.stream_thread = None

            self.API_KEY = ""
            self.SECRET_KEY = ""

            self.clear_interface_connections()

            self.graph_interval = "BTCUSDT"
            self.graph_interval = "1"

            self.user_interface = LoginInterface(self.database)
            self.user_interface.emitter_open_main_window.connect(self.run_main)
            self.setCentralWidget(self.user_interface.central_widget_register_window)

    def toggle_trading(self):
        if self.trading_thread.running is False:
            self.trading_thread.running = True
            print("Succesffully Started the Bot")
        else:
            self.trading_thread.running = False
    
    def set_interface_user_settings(self):
        self.user_interface.chosen_coin_menu_button.setText(self.graph_symbol)
        self.user_interface.update_min_qty(self.instrument_info['result']['list'][0]['lotSizeFilter']['minOrderQty'])
        self.user_interface.max_leverage = self.instrument_info['result']['list'][0]['leverageFilter']['maxLeverage']
        if self.API_KEY != "" and self.SECRET_KEY != "": 
            self.wallet_balance = asyncio.run(self.exchange_bot_data.get_wallet_balance())
            self.wallet_balance = float(self.wallet_balance['result']['list'][0]['totalEquity'])
            get_graph_coin_info = asyncio.run(self.exchange_bot_data.get_position_info(symbol=self.graph_symbol))
            self.graph_leverage = get_graph_coin_info['result']['list'][0]['leverage']
            self.user_interface.posIdxInfo = get_graph_coin_info['result']['list'][0]['positionIdx']
            if self.user_interface.posIdxInfo == 0:
                self.user_interface.leverage_main = self.graph_leverage
                self.user_interface.leverage_secondary = None
            elif self.user_interface.posIdxInfo == 1:
                self.user_interface.leverage_main = self.graph_leverage
                self.user_interface.leverage_secondary = get_graph_coin_info['result']['list'][1]['leverage']
            else:
                self.user_interface.leverage_secondary = self.graph_leverage
                self.user_interface.leverage_main = get_graph_coin_info['result']['list'][1]['leverage']
            self.user_interface.update_leverage_label()      

    def update_settings(self,user_data):
        #If Interval or Symbol for the Bot is changed, resubscribe with the new data and update the data for the Environment
        if self.bot_interval != user_data['account_settings']['bot_settings']['used_timeframe'] or self.bot_symbol != user_data['account_settings']['bot_settings']['trading_contract']:
            self.bot_symbol = user_data['account_settings']['bot_settings']['trading_contract']
            self.bot_interval = user_data['account_settings']['bot_settings']['used_timeframe']

            self.exchange_bot_data.unsubscribe_from_kline()
            self.exchange_bot_data.subscrbe_to_kline(self.bot_symbol,self.bot_interval)

            data = BybitHistoryData(category="linear",symbol=self.bot_symbol, interval=self.bot_interval)
            self.bot_df = pd.DataFrame(data.klines, columns=["open_time", "open_price", "high_price", "low_price", "close_price", "volume", "turnover"])
            self.live_env.df = self.bot_df
  
        if self.account_risk != user_data['account_settings']['bot_settings']['account_risk']:
            self.account_risk = user_data['account_settings']['bot_settings']['account_risk']
            self.live_env.accountRiskPercentage = self.account_risk

        #If risk risk updated change it for the env
        if self.risk_to_reward_string != self.user_data['account_settings']['bot_settings']['risk_to_reward']:
            self.risk_to_reward_string = self.user_data['account_settings']['bot_settings']['risk_to_reward']
            firstNum, secondNum = map(float, self.risk_to_reward_string.split(":"))
            risk_to_reward = secondNum / firstNum
            self.live_env.riskToRewardRatio = risk_to_reward    

        #The if statements checks if the used Exchange Bybit/Mexc is changed (ex Bybit to Mexc) 
        #or if the API Keys were empty and if that is the case it goes in to set exchang and keys
        if self.is_bybit_used != user_data['account_settings']['exchange_settings']['bybit_button_clicked'] or (self.API_KEY == "" and self.SECRET_KEY == ""):
            if (self.is_bybit_used and (user_data['account_settings']['exchange_settings']['bybit_api_key'] != ""
                                    or user_data['account_settings']['exchange_settings']['bybit_secret_key'] != "")):
                self.logout()
                
            elif (not self.is_bybit_used and (user_data['account_settings']['exchange_settings']['mexc_api_key'] != ""
                                    or user_data['account_settings']['exchange_settings']['mexc_secret_key'] != "")):
                self.logout()
        #The if statement checks if the API keys for the currently used exchange are changed
        if (self.is_bybit_used and (self.API_KEY != user_data['account_settings']['exchange_settings']['bybit_api_key'] 
                                    or self.SECRET_KEY != user_data['account_settings']['exchange_settings']['bybit_secret_key'])):
            self.logout()

        elif (not self.is_bybit_used and (self.API_KEY != user_data['account_settings']['exchange_settings']['mexc_api_key'] 
                                    or self.SECRET_KEY != user_data['account_settings']['exchange_settings']['mexc_secret_key'])):
            self.logout()



    def use_model_results(self, data):
        if (self.is_account_demo is False):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def _update_ui(data):
                new_state, reward, done, info = data
                if(info['Entered Trade']):
                    order_type = info['Current Trade']['Position Type']
                    take_profit = info['Current Trade']['Take Profit']
                    stop_loss = info['Current Trade']['Stop Loss']
                    quantity = info['Current Trade']['Quantity']
                    await self.exchange_bot_data.create_order(self.bot_symbol, order_type, 'Market',quantity,take_profit,stop_loss, 'Market')
            loop.run_until_complete(_update_ui(data))
        else:
            new_state, reward, done, info = data
            if(info['Entered Trade']):
                    order_type = info['Current Trade']['Position Type']
                    take_profit = info['Current Trade']['Take Profit']
                    stop_loss = info['Current Trade']['Stop Loss']
                    quantity = info['Current Trade']['Quantity']
                    print('Enter Demo Trade')

    def closeEvent(self, event):
        # self.data_stream.unsubscribe_kline()
        # self.data_stream.unsubscribe_ticker()
        self.trading_thread.stop()
        self.trading_thread.wait()  # Wait for the thread to finish
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
