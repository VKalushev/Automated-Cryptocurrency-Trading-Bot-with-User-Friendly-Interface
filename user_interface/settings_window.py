from PyQt5.QtWidgets import QMainWindow, QVBoxLayout,QGridLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QLineEdit,QMenu
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtCore import Qt
import asyncio

class AgreementWindow(QMainWindow):
    def __init__(self,parent=None):
        super().__init__(parent)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.setup_widgets()
        self.setup_css()

    def setup_widgets(self):
        self.layout_main = QVBoxLayout(self.central_widget)

        self.are_you_sure_message = QLabel('If you sure you want to continue with canceling the changes?')
        self.layout_main.addWidget(self.are_you_sure_message)

        self.second_row_widget = QWidget()
        self.second_row_layout = QHBoxLayout(self.second_row_widget)

        self.yes_button = QPushButton('Yes')
        self.no_button = QPushButton('No')

        self.yes_button.clicked.connect(self.close_if_clicked)
        self.no_button.clicked.connect(self.close_if_clicked)

        self.second_row_layout.addWidget(self.yes_button)
        self.second_row_layout.addWidget(self.no_button)

        self.layout_main.addWidget(self.second_row_widget)
        self.central_widget.setLayout(self.layout_main)

    def close_if_clicked(self):
        self.close()

    def setup_css(self):
        self.central_widget.setStyleSheet("background-color: #101014;")
        self.are_you_sure_message.setFixedHeight(30)
        self.are_you_sure_message.setAlignment(Qt.AlignHCenter)
        self.are_you_sure_message.setStyleSheet("font-size: 20px; border: none; color: #a8a8a8;")

        self.yes_button.setStyleSheet("""
                                    QPushButton { background-color: #101014; border: 2px solid #a8a8a8; color: #a8a8a8; font-family: BinancePlex, Arial; font-size: 16px; border-radius: 10px;} 
                                    QPushButton:pressed { background-color: #101014; border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 16px; border-radius: 10px;} 
                                    """)
        
        self.no_button.setStyleSheet("""
                                QPushButton { background-color: #101014; border: 2px solid #a8a8a8; color: #a8a8a8; font-family: BinancePlex, Arial; font-size: 16px; border-radius: 10px;} 
                                QPushButton:pressed { background-color: #101014; border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 16px; border-radius: 10px;} 
                                """)

class SettingsWindow(QMainWindow,QObject):
    emitter_update_data = pyqtSignal(object)

    def __init__(self, database,user_id,parent=None):
        super().__init__(parent)

        self.database = database
        self.user_data = database.accounts_collection.find_one({'_id': user_id})
        self.bot_settings = self.user_data['account_settings']['bot_settings']
        self.exchange_settings = self.user_data['account_settings']['exchange_settings']
        self.time_frame_text = self.convert_timeframe_to_text()
        self.central_widget = QWidget()
        self.is_changed_data_saved = False
        self.setCentralWidget(self.central_widget)
        self.setup_widgets()
        self.setup_css()

    def convert_timeframe_to_text(self):
        current = self.bot_settings['used_timeframe']
        if current == "1" or current == "Min1":
            return "1min"
        elif current == "5" or current == "Min5":
            return "5min"
        elif current == "15" or current == "Min15":
            return "15min"
        elif current == "30" or current == "Min30":
            return "30min"
        elif current == "60" or current == "Min60":
            return "1h"
        elif current == "240" or current == "Hour4":
            return "4h"
        elif current == "D" or current == "Day1":
            return "1D"
        elif current == "W" or current == "Week1":
            return "1W"
        elif current == "M" or current == "Month1":
            return "1M"
        else:
            return "1min"

    def setup_widgets(self):
        self.layout_main = QVBoxLayout(self.central_widget)


        #Section: Profile Settings:
        self.are_you_sure_message = QLabel('Profile Settings:')
        self.layout_main.addWidget(self.are_you_sure_message)

        self.profile_settings_widget = QWidget()
        self.profile_settings_layout = QHBoxLayout(self.profile_settings_widget)

        #Inner Section: Change Email ----------------------------------------------------------
        self.change_email_widget = QWidget()
        self.change_email_gridLayout = QGridLayout(self.change_email_widget)

        self.change_email_label = QLabel('Change Email Address:')
        self.change_email_gridLayout.addWidget(self.change_email_label,0,0)
        self.new_email_label = QLabel('New Email:')
        self.new_email_textbox = QLineEdit()
        self.new_email_textbox.setText("")
        self.change_email_gridLayout.addWidget(self.new_email_label,1,0)
        self.change_email_gridLayout.addWidget(self.new_email_textbox,1,1)
        
        self.confirm_email_label = QLabel("Confirm Email:")
        self.confirm_email_textbox = QLineEdit()
        self.confirm_email_textbox.setText("")
        self.change_email_gridLayout.addWidget(self.confirm_email_label,2,0)
        self.change_email_gridLayout.addWidget(self.confirm_email_textbox,2,1)

        self.email_error_message = QLabel('')
        self.email_error_message.hide()
        self.email_success_message = QLabel('')
        self.email_success_message.hide()

        self.change_email_gridLayout.addWidget(self.email_error_message,3,0,1,2)
        self.change_email_gridLayout.addWidget(self.email_success_message,3,0,1,2)
        self.profile_settings_layout.addWidget(self.change_email_widget)

        #Inner Section: Change Password ----------------------------------------------------------
        self.change_password_widget = QWidget()
        self.change_password_gridLayout = QGridLayout(self.change_password_widget)

        self.change_password_label = QLabel('Change Password:')
        self.change_password_gridLayout.addWidget(self.change_password_label,0,0)
        self.new_password_label = QLabel('New Password:')
        self.new_password_textbox = QLineEdit()
        self.new_password_textbox.setText("")
        self.change_password_gridLayout.addWidget(self.new_password_label,1,0)
        self.change_password_gridLayout.addWidget(self.new_password_textbox,1,1)
        
        self.confirm_password_label = QLabel("Confirm Password:")
        self.confirm_password_textbox = QLineEdit()
        self.confirm_password_textbox.setText("")
        self.change_password_gridLayout.addWidget(self.confirm_password_label,2,0)
        self.change_password_gridLayout.addWidget(self.confirm_password_textbox,2,1)

        self.password_error_message = QLabel('')
        self.password_error_message.hide()
        self.password_success_message = QLabel('')
        self.password_success_message.hide()

        self.change_password_gridLayout.addWidget(self.password_error_message,3,0,1,2)
        self.change_password_gridLayout.addWidget(self.password_success_message,3,0,1,2)

        self.profile_settings_layout.addWidget(self.change_password_widget)

        self.layout_main.addWidget(self.profile_settings_widget)
        #Section: Exchanges Settings ----------------------------------------------------------
        self.exchange_settings_label = QLabel('Exchange Settings:')
        self.layout_main.addWidget(self.exchange_settings_label)

        self.exchange_settings_widget = QWidget()
        self.exchange_settings_layout = QHBoxLayout(self.exchange_settings_widget)

        #Inner Section - Bybit
        self.bybit_exchange_settings_inner_widget = QWidget()
        self.bybit_exchange_settings_inner_gridLayout = QGridLayout(self.bybit_exchange_settings_inner_widget)

        self.bybit_exchange_label = QLabel('Bybit Exchange:')
        self.bybit_exchange_settings_inner_gridLayout.addWidget(self.bybit_exchange_label,0,0)
        self.bybit_api_key_label = QLabel('API-KEY:')
        self.bybit_api_key_textbox = QLineEdit()
        self.bybit_api_key_textbox.setText(self.exchange_settings['bybit_api_key'])
        self.bybit_exchange_settings_inner_gridLayout.addWidget(self.bybit_api_key_label,1,0)
        self.bybit_exchange_settings_inner_gridLayout.addWidget(self.bybit_api_key_textbox,1,1)
        
        self.bybit_secret_key_label = QLabel("Secret-key:")
        self.bybit_secret_key_textbox= QLineEdit()
        self.bybit_secret_key_textbox.setText(self.exchange_settings['bybit_secret_key'])
        self.bybit_exchange_settings_inner_gridLayout.addWidget(self.bybit_secret_key_label,2,0)
        self.bybit_exchange_settings_inner_gridLayout.addWidget(self.bybit_secret_key_textbox,2,1)

        self.bybit_set_as_active_button = QPushButton('Set ByBit as Active')
        self.bybit_set_as_active_button.setCheckable(True)
        self.bybit_set_as_active_button.setChecked(self.exchange_settings['bybit_button_clicked'])
        self.bybit_set_as_active_button.clicked.connect(self.bybit_button_clicked)
        self.bybit_exchange_settings_inner_gridLayout.addWidget(self.bybit_set_as_active_button,3,0,1,2)

        self.bybit_error_message = QLabel('')
        self.bybit_error_message.hide()
        self.bybit_success_message = QLabel('')
        self.bybit_success_message.hide()

        self.bybit_exchange_settings_inner_gridLayout.addWidget(self.bybit_error_message,4,0,1,2)
        self.bybit_exchange_settings_inner_gridLayout.addWidget(self.bybit_success_message,4,0,1,2)

        self.exchange_settings_layout.addWidget(self.bybit_exchange_settings_inner_widget)

        #Inner Section - MEXC
        self.mexc_exchange_settings_inner_widget = QWidget()
        self.mexc_exchange_settings_inner_gridLayout = QGridLayout(self.mexc_exchange_settings_inner_widget)

        self.mexc_exchange_label = QLabel('MEXC - NOT SUPPORTED YET:')
        self.mexc_exchange_settings_inner_gridLayout.addWidget(self.mexc_exchange_label,0,0)
        self.mexc_api_key_label = QLabel('API-KEY:')
        self.mexc_api_key_textbox = QLineEdit()
        self.mexc_api_key_textbox.setText(self.exchange_settings['mexc_api_key'])
        self.mexc_exchange_settings_inner_gridLayout.addWidget(self.mexc_api_key_label,1,0)
        self.mexc_exchange_settings_inner_gridLayout.addWidget(self.mexc_api_key_textbox,1,1)
        
        self.mexc_secret_key_label = QLabel("Secret-key:")
        self.mexc_secret_key_textbox= QLineEdit()
        self.mexc_secret_key_textbox.setText(self.exchange_settings['mexc_secret_key'])
        self.mexc_exchange_settings_inner_gridLayout.addWidget(self.mexc_secret_key_label,2,0)
        self.mexc_exchange_settings_inner_gridLayout.addWidget(self.mexc_secret_key_textbox,2,1)

        self.mexc_set_as_active_button = QPushButton('Set MEXC as Active')
        self.mexc_set_as_active_button.setCheckable(True)
        self.mexc_set_as_active_button.setChecked(not self.exchange_settings['bybit_button_clicked'])
        self.mexc_set_as_active_button.clicked.connect(self.mexc_button_clicked)
        self.mexc_exchange_settings_inner_gridLayout.addWidget(self.mexc_set_as_active_button,3,0,1,2)

        self.mexc_error_message = QLabel('')
        self.mexc_error_message.hide()
        self.mexc_success_message = QLabel('')
        self.mexc_success_message.hide()

        self.mexc_exchange_settings_inner_gridLayout.addWidget(self.mexc_error_message,4,0,1,2)
        self.mexc_exchange_settings_inner_gridLayout.addWidget(self.mexc_success_message,4,0,1,2)

        self.exchange_settings_layout.addWidget(self.mexc_exchange_settings_inner_widget)
        self.layout_main.addWidget(self.exchange_settings_widget)
        #Section: Bot Settings ----------------------------------------------------------
        self.bot_settings_label = QLabel('Bot Settings:')
        self.layout_main.addWidget(self.bot_settings_label)

        self.bot_settings_widget = QWidget()
        self.bot_settings_layout = QHBoxLayout(self.bot_settings_widget)

        #Inner Section - Left Side 
        self.bot_settings_inner_widget_left_side = QWidget()
        self.bot_settings_inner_gridLayout_left_side = QGridLayout(self.bot_settings_inner_widget_left_side)

        self.coin_to_trade_label = QLabel('Trading Contract:')
        self.coin_to_trade_textbox = QLineEdit()
        self.coin_to_trade_textbox.setText(self.bot_settings['trading_contract'])
        self.bot_settings_inner_gridLayout_left_side.addWidget(self.coin_to_trade_label,0,0)
        self.bot_settings_inner_gridLayout_left_side.addWidget(self.coin_to_trade_textbox,0,1)

        self.trading_time_frame_label = QLabel('Used timeframe by bot:')
        self.generate_menu()

        self.bot_settings_inner_gridLayout_left_side.addWidget(self.trading_time_frame_label,1,0)
        self.bot_settings_layout.addWidget(self.bot_settings_inner_widget_left_side)

        #Inner Section - Right Side 
        self.bot_settings_inner_widget_right_side = QWidget()
        self.bot_settings_inner_gridLayout_right_side = QGridLayout(self.bot_settings_inner_widget_right_side)

        self.risk_to_reward_ratio_label = QLabel('Minimal Risk to Reward Ratio:')
        self.risk_to_reward_ratio_textbox = QLineEdit()
        self.risk_to_reward_ratio_textbox.setText(self.bot_settings['risk_to_reward'])
        self.bot_settings_inner_gridLayout_right_side.addWidget(self.risk_to_reward_ratio_label,0,0)
        self.bot_settings_inner_gridLayout_right_side.addWidget(self.risk_to_reward_ratio_textbox,0,1)

        self.account_risk_label = QLabel('Percentage Account Balance Risk:')
        self.account_risk_textbox = QLineEdit()
        self.account_risk_textbox.setText(self.bot_settings['account_risk'])
        self.bot_settings_inner_gridLayout_right_side.addWidget(self.account_risk_label,1,0)
        self.bot_settings_inner_gridLayout_right_side.addWidget(self.account_risk_textbox,1,1)

        self.bot_settings_layout.addWidget(self.bot_settings_inner_widget_right_side)
        self.layout_main.addWidget(self.bot_settings_widget)

        self.buttons_widget = QWidget()
        self.buttons_layout = QHBoxLayout(self.buttons_widget)

        self.save_button = QPushButton("Save Changes")
        self.cancel_button = QPushButton("Cancel")

        self.save_button.clicked.connect(self.save_button_clicked)
        self.cancel_button.clicked.connect(self.cancel_button_clicked)

        self.buttons_layout.addWidget(self.save_button)
        self.buttons_layout.addWidget(self.cancel_button)
        
        self.layout_main.addWidget(self.buttons_widget)
        self.central_widget.setLayout(self.layout_main)

    def changeTimeFrame(self, coin_name):
         self.bybit_chosen_timeframe_menu_button.setText(coin_name)
    
    

    def save_button_clicked(self):
        
        if self.new_email_textbox.text() != "":
            if(self.new_email_textbox.text() == self.confirm_email_textbox.text()):
                if(self.new_email_textbox.text() != self.user_data['email']):
                    result = self.database.change_email(self.user_data,self.new_email_textbox.text())

                    if result['bool']:
                        self.is_changed_data_saved = True
                        self.user_data['email'] = self.new_email_textbox.text()
                        self.email_error_message.hide()
                        self.email_success_message.setText(result['message'])
                        self.email_success_message.show()
                    else:
                        self.email_success_message.hide()
                        self.email_error_message.setText(result['message'])
                        self.email_error_message.show()
                else:
                    self.email_success_message.hide()
                    self.email_error_message.setText('The new Email must be different from the old one')
                    self.email_error_message.show()                   
            else:
                self.email_success_message.hide()
                self.email_error_message.setText('The entered Emails do not match')
                self.email_error_message.show()

        if self.new_password_textbox.text() != "":

            if self.new_password_textbox.text() == self.new_password_textbox.text():
                    result = self.database.change_password(self.user_data,self.new_password_textbox.text())
                    if result['bool']:
                        self.is_changed_data_saved = True
                        self.user_data['password'] = self.new_password_textbox.text()
                        self.password_error_message.hide()
                        self.password_success_message.setText(result['message'])
                        self.password_success_message.show()
                    else:
                        self.password_success_message.hide()
                        self.password_error_message.setText(result['message'])
                        self.password_error_message.show()
            else:
                self.password_success_message.hide()
                self.password_error_message.setText('The entered Passwords do not match')
                self.password_error_message.show()

        if self.bybit_api_key_textbox.text() != self.exchange_settings['bybit_api_key'] or self.bybit_secret_key_textbox.text() != self.exchange_settings['bybit_secret_key']:

            async def change_api_keys():
                result = await self.database.change_bybit_api_keys(self.user_data,self.bybit_api_key_textbox.text(),self.bybit_secret_key_textbox.text())
                return result
            
            if self.bybit_api_key_textbox.text() != "" and self.bybit_secret_key_textbox.text() != "":
                result = asyncio.run(change_api_keys())

                if result['bool']:
                    self.is_changed_data_saved = True
                    self.user_data = result['data']
                    self.bybit_error_message.hide()
                    self.bybit_success_message.setText(result['message'])
                    self.bybit_success_message.show()
                else:
                    self.bybit_success_message.hide()
                    self.bybit_error_message.setText(result['message'])
                    self.bybit_error_message.show()
            else:
                result = self.database.clear_bybit_keys(self.user_data)

                if result['bool']:
                    self.is_changed_data_saved = True
                    self.user_data = result['data']
                    self.bybit_error_message.hide()
                    self.bybit_success_message.setText(result['message'])
                    self.bybit_success_message.show()
                else:
                    self.bybit_success_message.hide()
                    self.bybit_error_message.setText(result['message'])
                    self.bybit_error_message.show()


        if self.mexc_api_key_textbox.text() != self.exchange_settings['mexc_api_key'] or self.mexc_secret_key_textbox.text() != self.exchange_settings['mexc_secret_key']:

            async def change_api_keys():
                result = await self.database.change_mexc_api_keys(self.user_data,self.mexc_api_key_textbox.text(),self.mexc_secret_key_textbox.text())
                return result
            if self.mexc_api_key_textbox.text() != "" and self.mexc_secret_key_textbox.text() != "":
                result = asyncio.run(change_api_keys())

                if result['bool']:
                    print("Entered for new API MEXC")
                    self.is_changed_data_saved = True
                    self.user_data = result['data']
                    self.mexc_error_message.hide()
                    self.mexc_success_message.setText(result['message'])
                    self.mexc_success_message.show()
                else:
                    self.mexc_success_message.hide()
                    self.mexc_error_message.setText(result['message'])
                    self.mexc_error_message.show()
            else:
                result = self.database.clear_mexc_keys(self.user_data)

                if result['bool']:
                    self.is_changed_data_saved = True
                    self.user_data = result['data']
                    self.mexc_error_message.hide()
                    self.mexc_success_message.setText(result['message'])
                    self.mexc_success_message.show()
                else:
                    self.mexc_success_message.hide()
                    self.mexc_error_message.setText(result['message'])
                    self.mexc_error_message.show()
        # if self.bybit_set_as_active_button != self.exchange_settings['bybit_button_clicked']:
        #     result = self.database.update_active_exchange(self.user_data)

        #     if result['bool']:
        #         print("Entered for BUTTON")
        #         is_any_user_data_changed = True
        #         self.user_data = result['data']
        #         # print(result['message'])
        #     else:
        #         print(result['message'])

        if self.get_time_frame_text() != self.bot_settings['used_timeframe']:
            result = self.database.update_used_timeframe(self.user_data,self.get_time_frame_text())

            if result['bool']:
                print("Entered for new TIMEFRAME")
                self.is_changed_data_saved = True
                self.user_data = result['data']
            
            print(result['message'])


        
        if self.coin_to_trade_textbox.text() != self.bot_settings['trading_contract']:
            result = self.database.update_trading_contract(self.user_data,self.coin_to_trade_textbox.text())

            if result['bool']:
                self.is_changed_data_saved = True
                self.user_data = result['data']
            
            print(result['message'])


        if self.risk_to_reward_ratio_textbox.text() != self.bot_settings['risk_to_reward']:
            result = self.database.update_risk_to_reward(self.user_data,self.risk_to_reward_ratio_textbox.text())

            if result['bool']:
                self.is_changed_data_saved = True
                self.user_data = result['data']
            
            print(result['message'])

        if self.account_risk_textbox.text() != self.bot_settings['account_risk']:
            result = self.database.update_account_risk(self.user_data,self.account_risk_textbox.text())

            if result['bool']:
                self.is_changed_data_saved = True
                self.user_data = result['data']
            
            print(result['message'])

        if(self.is_changed_data_saved):
            self.is_changed_data_saved = False
            self.bot_settings = self.user_data['account_settings']['bot_settings']
            self.exchange_settings = self.user_data['account_settings']['exchange_settings']
            self.emitter_update_data.emit(self.user_data)

    def get_time_frame_text(self):
        if self.bybit_chosen_timeframe_menu_button.text() == "1m":
            if self.bybit_set_as_active_button.isChecked():
                return "1"
            else:
                return "Min1"
        elif self.bybit_chosen_timeframe_menu_button.text() == "5m":
            if self.bybit_set_as_active_button.isChecked():
                return "5"
            else:
                return "Min5"
        elif self.bybit_chosen_timeframe_menu_button.text() == "15m":
            if self.bybit_set_as_active_button.isChecked():
                return "15"
            else:
                return "Min15"
        elif self.bybit_chosen_timeframe_menu_button.text() == "30m":
            if self.bybit_set_as_active_button.isChecked():
                return "30"
            else:
                return "Min30"
        elif self.bybit_chosen_timeframe_menu_button.text() == "1h":
            if self.bybit_set_as_active_button.isChecked():
                return "60"
            else:
                return "Min60"
        elif self.bybit_chosen_timeframe_menu_button.text() == "4h":
            if self.bybit_set_as_active_button.isChecked():
                return "240"
            else:
                return "Hour4"
        elif self.bybit_chosen_timeframe_menu_button.text() == "1D":
            if self.bybit_set_as_active_button.isChecked():
                return "D"
            else:
                return "Day1"
        elif self.bybit_chosen_timeframe_menu_button.text() == "1W":
            if self.bybit_set_as_active_button.isChecked():
                return "W"
            else:
                return "Week1"
        elif self.bybit_chosen_timeframe_menu_button.text() == "1M":
            if self.bybit_set_as_active_button.isChecked():
                return "M"
            else:
                return "Month1"
        else:
            if self.bybit_set_as_active_button.isChecked():
                return "5"
            else:
                return "Min5"
        

    def cancel_button_clicked(self):
        if (self.new_email_textbox.text() != "" or self.confirm_email_textbox.text() != ""
            or self.new_password_textbox.text() !="" or self.confirm_password_textbox.text() != "" 
            or self.bybit_api_key_textbox.text() != self.exchange_settings['bybit_api_key'] or self.bybit_secret_key_textbox.text() != self.exchange_settings['bybit_api_key'] 
            or self.mexc_api_key_textbox.text() != self.exchange_settings['mexc_api_key'] or self.mexc_secret_key_textbox.text() != self.exchange_settings['mexc_api_key'] 
            or self.coin_to_trade_textbox.text() != self.bot_settings['trading_contract'] or self.risk_to_reward_ratio_textbox.text() != self.bot_settings['risk_to_reward'] 
            # or self.trading_time_frame_textbox.text() != self.bot_settings['used_timeframe']):
            or self.bybit_chosen_timeframe_menu_button.text() != self.bot_settings['used_timeframe']):

            if self.is_changed_data_saved:
                ask_if_sure = AgreementWindow(self.central_widget)
                ask_if_sure.show()
                ask_if_sure.yes_button.clicked.connect(self.close_window)
            else:
                self.close()
        else:
            self.close()

    def close_window(self):
        self.close()

    def bybit_button_clicked(self):
        self.bybit_set_as_active_button.setChecked(True)
        if(self.mexc_set_as_active_button.isChecked()):
            self.mexc_set_as_active_button.setChecked(False)
            self.generate_menu()

    def mexc_button_clicked(self):
        # self.mexc_set_as_active_button.setChecked(True)
        self.mexc_set_as_active_button.setChecked(False)
        self.mexc_error_message.setText('Currently Unavailable')
        # self.mexc_error_message.show
        if(self.bybit_set_as_active_button.isChecked()):
            # self.bybit_set_as_active_button.setChecked(False)
            self.generate_menu()

    def generate_menu(self):
        # Check if the button exists before attempting to remove it
        if hasattr(self, 'bybit_chosen_timeframe_menu_button'):
            # Clear the layout before adding the new widget
            for i in reversed(range(self.bot_settings_inner_gridLayout_left_side.count())):
                widget = self.bot_settings_inner_gridLayout_left_side.itemAt(i).widget()

                if widget and widget == self.bybit_chosen_timeframe_menu_button:
                    self.bot_settings_inner_gridLayout_left_side.removeWidget(widget)
                    widget.deleteLater()

        self.bybit_chosen_timeframe_menu_button = QPushButton(self.time_frame_text)
        self.bybit_interval_menu = QMenu(self.bybit_chosen_timeframe_menu_button)
        if self.bybit_set_as_active_button.isChecked():
            self.bybit_interval_menu.addAction("1m")
            self.bybit_interval_menu.addAction("5m")
            self.bybit_interval_menu.addAction("15m")
            self.bybit_interval_menu.addAction("30m")
            self.bybit_interval_menu.addAction("1h")
            self.bybit_interval_menu.addAction("4h")
            self.bybit_interval_menu.addAction("1D")
            self.bybit_interval_menu.addAction("1W")
            self.bybit_interval_menu.addAction("1M")
        else:
            self.bybit_interval_menu.addAction("TODO") 

        # Connect the triggered signal of the coin menu actions to the changeCoin function
        for action in self.bybit_interval_menu.actions():
            action.triggered.connect(lambda checked, text=action.text(): self.changeTimeFrame(text))
        self.bybit_chosen_timeframe_menu_button.setMenu(self.bybit_interval_menu)
        self.bot_settings_inner_gridLayout_left_side.addWidget(self.bybit_chosen_timeframe_menu_button,1,1)
        self.fix_textbox(self.trading_time_frame_label,self.bybit_chosen_timeframe_menu_button)


    
    def setup_css(self):
        self.fix_textbox(self.new_email_label,self.new_email_textbox)
        self.fix_textbox(self.confirm_email_label,self.confirm_email_textbox)
        self.fix_textbox(self.new_password_label,self.new_password_textbox)
        self.fix_textbox(self.confirm_password_label,self.confirm_password_textbox)
        self.fix_textbox(self.bybit_api_key_label,self.bybit_api_key_textbox)
        self.fix_textbox(self.bybit_secret_key_label,self.bybit_secret_key_textbox)
        self.fix_textbox(self.mexc_api_key_label,self.mexc_api_key_textbox)
        self.fix_textbox(self.mexc_secret_key_label,self.mexc_secret_key_textbox)
        self.fix_textbox(self.coin_to_trade_label,self.coin_to_trade_textbox)
        self.fix_textbox(self.trading_time_frame_label,self.bybit_chosen_timeframe_menu_button)
        self.fix_textbox(self.risk_to_reward_ratio_label,self.risk_to_reward_ratio_textbox)
        self.fix_textbox(self.account_risk_label,self.account_risk_textbox)

        self.new_password_textbox.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_textbox.setEchoMode(QLineEdit.EchoMode.Password)

        self.mexc_exchange_settings_inner_widget.setStyleSheet("border: none;")
        self.bot_settings_inner_widget_right_side.setStyleSheet("border: none;")
        self.bot_settings_inner_widget_left_side.setStyleSheet("border: none;")
        self.bybit_exchange_settings_inner_widget.setStyleSheet("border: none; ")
        self.change_password_widget.setStyleSheet("border: none;")
        self.change_email_widget.setStyleSheet("border: none;")
        
        self.central_widget.setStyleSheet("background-color: #101014;")
        self.are_you_sure_message.setStyleSheet("font-size: 20px; border: none; color: #a8a8a8;")
        self.exchange_settings_label.setStyleSheet("font-size: 20px; border: none; color: #a8a8a8;")
        self.bot_settings_label.setStyleSheet("font-size: 20px; border: none; color: #a8a8a8;")
        self.email_error_message.setStyleSheet("font-size: 12px; border: none; color: red;")
        self.email_success_message.setStyleSheet("font-size: 12px; border: none; color: green;")
        self.password_error_message.setStyleSheet("font-size: 12px; border: none; color: red;")
        self.password_success_message.setStyleSheet("font-size: 12px; border: none; color: green;")
        self.bybit_error_message.setStyleSheet("font-size: 12px; border: none; color: red;")
        self.bybit_success_message.setStyleSheet("font-size: 12px; border: none; color: green;")
        self.mexc_error_message.setStyleSheet("font-size: 12px; border: none; color: red;")
        self.mexc_success_message.setStyleSheet("font-size: 12px; border: none; color: green;")

        self.mexc_set_as_active_button.setStyleSheet("""
                                    QPushButton { background-color: #101014; border: 2px solid #a8a8a8; color: #a8a8a8; font-family: BinancePlex, Arial; font-size: 16px; border-radius: 10px;} 
                                    QPushButton:pressed { background-color: #101014; border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 16px; border-radius: 10px;} 
                                    QPushButton:checked { background-color: #101014; border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 16px; border-radius: 10px;}
                                    """)
        self.bybit_set_as_active_button.setStyleSheet("""
                                    QPushButton { background-color: #101014; border: 2px solid #a8a8a8; color: #a8a8a8; font-family: BinancePlex, Arial; font-size: 16px; border-radius: 10px;} 
                                    QPushButton:pressed { background-color: #101014; border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 16px; border-radius: 10px;} 
                                    QPushButton:checked { background-color: #101014; border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 16px; border-radius: 10px;}
                                    """)
        
        self.cancel_button.setStyleSheet("""
                                    QPushButton { background-color: #101014; border: 2px solid #a8a8a8; color: #a8a8a8; font-family: BinancePlex, Arial; font-size: 16px; border-radius: 10px;} 
                                    QPushButton:pressed { background-color: #101014; border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 16px; border-radius: 10px;} 
                                    """)
        self.cancel_button.setFixedWidth(100)
        self.buttons_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.save_button.setFixedWidth(130)
        self.save_button.setStyleSheet("""
                                    QPushButton { background-color: #101014; border: 2px solid #a8a8a8; color: #a8a8a8; font-family: BinancePlex, Arial; font-size: 16px; border-radius: 10px;} 
                                    QPushButton:pressed { background-color: #101014; border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 16px; border-radius: 10px;} 
                                    """)
        
        self.profile_settings_widget.setStyleSheet("background-color: #08080a; color: #a8a8a8; font-size: 16px; border: 1px solid #333333; border-radius: 5px; font-family: BinancePlex, Arial;")
        self.exchange_settings_widget.setStyleSheet("background-color: #08080a; color: #a8a8a8; font-size: 16px; border: 1px solid #333333; border-radius: 5px; font-family: BinancePlex, Arial;")
        self.bot_settings_widget.setStyleSheet("background-color: #08080a; color: #a8a8a8; font-size: 16px; border: 1px solid #333333; border-radius: 5px; font-family: BinancePlex, Arial;")

    def fix_textbox(self,label,textbox):
        label.setStyleSheet("background-color: #08080a; color: #a8a8a8; font-size: 12px; font-family: BinancePlex, Arial;")
        textbox.setStyleSheet("background-color: #08080a; color: #a8a8a8; font-size: 12px; border: 1px solid #333333; border-radius: 5px; font-family: BinancePlex, Arial;")
        label.setFixedWidth(130)
        label.setFixedHeight(30)
        textbox.setFixedWidth(150)
        textbox.setFixedHeight(label.sizeHint().height())
