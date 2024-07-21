from PyQt5.QtWidgets import QMainWindow,QGridLayout, QWidget, QLabel, QPushButton,QLineEdit,QCheckBox 
from PyQt5.QtCore import Qt

class RegisterWindow(QMainWindow):
    def __init__(self, database,parent=None):
        super().__init__(parent)
        self.setGeometry(1160, 465,0,0)

        self.database = database

        # Set up the settings window layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.setup_widgets()
        self.setup_css()

    def setup_widgets(self):
        self.gridLayout_main = QGridLayout(self.central_widget)
        self.inner_widget = QWidget()
        self.inner_gridLayout = QGridLayout(self.inner_widget)
        self.create_account = QLabel('Create an account')

        
        self.name = QLabel('Name:')
        self.name_textbox = QLineEdit()

        self.email = QLabel('Email:')
        self.email_textbox = QLineEdit()

        self.username_label = QLabel('Username:')
        self.username_textbox = QLineEdit()

        self.password = QLabel('Password:')
        self.password_textbox = QLineEdit()

        self.confirm_password = QLabel('Confirm Password:')
        self.confirm_password_textbox = QLineEdit()

        self.error_creating_account = QLabel('Error: Password too short it should be at least 7 characters.')
        self.error_creating_account.hide()

        self.successfully_created_account = QLabel('Account was successfully created now proceed to login.')
        self.successfully_created_account.hide()

        self.create_account_button = QPushButton('Create Account')
        self.create_account_button.clicked.connect(self.create_account_button_clicked)

        self.checkbox = QCheckBox('Make Account Demo')

        self.inner_gridLayout.addWidget(self.create_account,0,0,1,2)
        self.inner_gridLayout.addWidget(self.name,1,0)
        self.inner_gridLayout.addWidget(self.name_textbox,1,1)
        self.inner_gridLayout.addWidget(self.email,2,0)
        self.inner_gridLayout.addWidget(self.email_textbox,2,1)
        self.inner_gridLayout.addWidget(self.username_label,3,0)
        self.inner_gridLayout.addWidget(self.username_textbox,3,1)
        self.inner_gridLayout.addWidget(self.password,4,0)
        self.inner_gridLayout.addWidget(self.password_textbox,4,1)
        self.inner_gridLayout.addWidget(self.confirm_password,5,0)
        self.inner_gridLayout.addWidget(self.confirm_password_textbox,5,1)
        self.inner_gridLayout.addWidget(self.error_creating_account,6,0,1,2)
        self.inner_gridLayout.addWidget(self.successfully_created_account,6,0,1,2)  
        self.inner_gridLayout.addWidget(self.checkbox,7,0,1,2)
        self.inner_gridLayout.addWidget(self.create_account_button,8,0,1,2)

        self.gridLayout_main.addWidget(self.inner_widget)
        self.central_widget.setLayout(self.gridLayout_main)

    def create_account_button_clicked(self):
        data = {'name':self.name_textbox.text(), 'email':self.email_textbox.text(),
                'username':self.username_textbox.text(), 'password':self.password_textbox.text(),
                'confirmation-password':self.confirm_password_textbox.text(), 'is_account_demo':self.checkbox.isChecked()}
        
        result = self.database.check_register_input_validity(data)
        # print(result)
        if result['bool']:
            self.error_creating_account.hide()
            self.successfully_created_account.show()
        else:
            self.error_creating_account.setText(result['message'])
            self.successfully_created_account.hide()
            self.error_creating_account.show()
        

    def setup_css(self):        
        self.name.setFixedWidth(80)
        self.name.setFixedHeight(30)
        self.email.setFixedWidth(80)
        self.email.setFixedHeight(30)
        self.username_label.setFixedWidth(80)
        self.username_label.setFixedHeight(30)
        self.password.setFixedWidth(80)
        self.password.setFixedHeight(30)
        self.confirm_password.setFixedWidth(110)
        self.confirm_password.setFixedHeight(30)

        self.name_textbox.setFixedHeight(self.name.sizeHint().height())
        self.email_textbox.setFixedHeight(self.email.sizeHint().height())
        self.username_textbox.setFixedHeight(self.username_label.sizeHint().height())
        self.password_textbox.setFixedHeight(self.password.sizeHint().height())
        self.confirm_password_textbox.setFixedHeight(self.confirm_password.sizeHint().height())

        self.name_textbox.setFixedWidth(150)
        self.email_textbox.setFixedWidth(150)
        self.username_textbox.setFixedWidth(150)
        self.password_textbox.setFixedWidth(150)
        self.confirm_password_textbox.setFixedWidth(150)

        self.password_textbox.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_textbox.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.create_account.setFixedHeight(30)
        self.create_account.setAlignment(Qt.AlignHCenter)
        self.create_account.setStyleSheet('border: none; font-size: 24px;')

        self.successfully_created_account.setFixedHeight(30)
        self.successfully_created_account.setAlignment(Qt.AlignHCenter)
        self.successfully_created_account.setStyleSheet("color: green; border: none;")

        self.error_creating_account.setAlignment(Qt.AlignHCenter)
        self.error_creating_account.setFixedHeight(30)
        self.error_creating_account.setStyleSheet("color: red; border: none;")

        self.name.setStyleSheet("background-color: #08080a; color: #a8a8a8; font-size: 12px; border: 1px solid #333333; border-radius: 5px; font-family: BinancePlex, Arial;")
        self.email.setStyleSheet("background-color: #08080a; color: #a8a8a8; font-size: 12px; border: 1px solid #333333; border-radius: 5px; font-family: BinancePlex, Arial;")
        self.username_label.setStyleSheet("background-color: #08080a; color: #a8a8a8; font-size: 12px; border: 1px solid #333333; border-radius: 5px; font-family: BinancePlex, Arial;")
        self.password.setStyleSheet("background-color: #08080a; color: #a8a8a8; font-size: 12px; border: 1px solid #333333; border-radius: 5px; font-family: BinancePlex, Arial;")
        self.confirm_password.setStyleSheet("background-color: #08080a; color: #a8a8a8; font-size: 12px; border: 1px solid #333333; border-radius: 5px; font-family: BinancePlex, Arial;")

        self.create_account_button.setStyleSheet("""
                                QPushButton { background-color: #101014; border: 2px solid #a8a8a8; color: #a8a8a8; font-family: BinancePlex, Arial; font-size: 20px; border-radius: 10px;} 
                                QPushButton:pressed { background-color: #101014; border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 20px; border-radius: 10px;} 
                                """)

        self.inner_widget.setStyleSheet("background-color: #08080a; color: #a8a8a8; font-size: 12px; border: 1px solid #333333; border-radius: 5px; font-family: BinancePlex, Arial;")
        self.central_widget.setStyleSheet("background-color: #101014;")