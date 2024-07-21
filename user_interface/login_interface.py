
from PyQt5.QtWidgets import QVBoxLayout,QHBoxLayout, QWidget, QLabel, QPushButton,QLineEdit
from PyQt5.QtCore import Qt,pyqtSignal,QObject
from user_interface.register_window import RegisterWindow

class LoginInterface(QObject):
    emitter_open_main_window = pyqtSignal(object)
    def __init__(self,database):
        super().__init__()
        self.database = database
        self.setup_login_window()
        self.setup_login_window_css()

    def setup_login_window(self):
        self.login_window_layout = QVBoxLayout()

        self.login_box_widget = QWidget()
        self.login_box_layout = QVBoxLayout(self.login_box_widget)

        self.trading_bot_label = QLabel('Trading Bot')
        self.login_box_layout.addWidget(self.trading_bot_label)

        self.username_widget = QWidget()
        self.username_layout = QHBoxLayout(self.username_widget)
        self.login_username_label = QLabel('Username: ')
        self.login_username_textbox = QLineEdit()

        self.password_widget = QWidget()
        self.password_layout = QHBoxLayout(self.password_widget)
        self.login_password_label = QLabel('Password: ')
        self.login_password_textbox = QLineEdit()

        self.username_layout.addWidget(self.login_username_label)
        self.username_layout.addWidget(self.login_username_textbox)
        self.password_layout.addWidget(self.login_password_label)
        self.password_layout.addWidget(self.login_password_textbox)

        self.login_box_layout.addWidget(self.username_widget)
        self.login_box_layout.addWidget(self.password_widget)

        self.error_message = QLabel('Error: The username or password are incorrect')
        self.error_message.hide()
        self.login_box_layout.addWidget(self.error_message)
        

        self.login_button = QPushButton('Login')
        self.login_button.clicked.connect(self.login_button_clicked)
        self.register_button = QPushButton('Register')
        self.register_button.clicked.connect(self.open_register_window)

        self.login_box_layout.addWidget(self.login_button)
        self.login_box_layout.addWidget(self.register_button)
        
        self.login_window_layout.addWidget(self.login_box_widget)

        self.central_widget_register_window = QWidget()
        self.central_widget_register_window.setLayout(self.login_window_layout)

    def setup_login_window_css(self):
        self.username_widget.setFixedHeight(50)
        self.password_widget.setFixedHeight(50)

        self.login_username_label.setFixedWidth(80)
        self.login_username_label.setFixedHeight(30)
        self.login_password_label.setFixedWidth(80)
        self.login_password_label.setFixedHeight(30)

        self.login_username_textbox.setFixedHeight(self.login_username_label.sizeHint().height())
        self.login_password_textbox.setFixedHeight(self.login_password_label.sizeHint().height())

        self.login_username_textbox.setFixedWidth(150)

        self.login_password_textbox.setFixedWidth(150)

        self.login_password_textbox.setEchoMode(QLineEdit.EchoMode.Password)

        self.error_message.setStyleSheet("color: red; margin: 0px 0px 0px 0px; border: none;")
        self.error_message.setFixedHeight(25)
        self.error_message.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.login_button.setStyleSheet("""
                                    QPushButton { background-color: #101014; border: 2px solid #a8a8a8; margin: 0px 25px 5px 25px; color: #a8a8a8; font-family: BinancePlex, Arial; font-size: 20px; border-radius: 10px;} 
                                    QPushButton:pressed { background-color: #101014; border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 20px; border-radius: 10px;} 
                                    """)
        
        self.register_button.setStyleSheet("""
                                    QPushButton { background-color: #101014; border: 2px solid #a8a8a8; color: #a8a8a8; font-family: BinancePlex, Arial; font-size: 20px; border-radius: 10px;} 
                                    QPushButton:pressed { background-color: #101014; border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 20px; border-radius: 10px;} 
                                    """)
        
        self.central_widget_register_window.setStyleSheet("background-color: #101014;")
        
        self.trading_bot_label.setStyleSheet('border: none; font-size: 24px;')
        
        self.trading_bot_label.setFixedHeight(30)
        self.trading_bot_label.setAlignment(Qt.AlignHCenter)

        # self.trading_bot_label.setAlignment(Qt.AlignVCenter)
        self.login_box_widget.setStyleSheet("background-color: #08080a; color: #a8a8a8; font-size: 12px; border: 1px solid #333333; border-radius: 5px; font-family: BinancePlex, Arial;")
        self.login_box_widget.setFixedWidth(300)
        self.login_box_widget.setFixedHeight(300)

        

        self.login_window_layout.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.login_password_textbox.setStyleSheet("padding: 1px 1px;")

    def login_button_clicked(self):
        user_data = {'username': self.login_username_textbox.text(), 'password':self.login_password_textbox.text()}
        result = self.database.attempt_to_login(user_data)

        if(result['bool']):
            self.user_data = result['data']
            self.user_id = result['data']['_id']
            self.error_message.hide()
            self.emitter_open_main_window.emit(self.user_data)
        else:
            self.error_message.show()


    def open_register_window(self):
        register_window = RegisterWindow(self.database,self.central_widget_register_window)
        register_window.show()