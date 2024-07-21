from PyQt5.QtWidgets import QMainWindow, QVBoxLayout,QGridLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QLineEdit, QSlider,QSpinBox,QSizePolicy, QStackedWidget
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtCore import Qt
import asyncio


class TradingSettingsWindow(QMainWindow,QObject):
    emitter_confirm_button_clicked = pyqtSignal(object)

    def __init__(self, leverage_main, leverage_secondary, max_leverage, parent=None):
        super().__init__(parent)
        self.leverage_main = leverage_main
        self.leverage_secondary = leverage_secondary
        max_leverage = max_leverage.split('.')
        self.max_leverage = int(max_leverage[0])

        if leverage_secondary is None:
            self.current_mode = "Original Mode"
        else:
            self.current_mode = "Hedge Mode"

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.setup_widgets()
        self.setup_css()

    def setup_widgets(self):
        self.layout_main = QVBoxLayout(self.central_widget)

        self.trading_settings_label = QLabel("Position Settings")
        self.layout_main.addWidget(self.trading_settings_label)

        self.mode_buttons_widget = QWidget()
        self.mode_buttons_layout = QHBoxLayout(self.mode_buttons_widget)
        self.original_mode_button = QPushButton("Original Mode")
        self.hedge_mode_button = QPushButton("Hedge Mode")

        self.original_mode_button.setCheckable(True)
        self.hedge_mode_button.setCheckable(True)

        self.original_mode_button.clicked.connect(self.mode_button_clicked)
        self.hedge_mode_button.clicked.connect(self.mode_button_clicked)

        self.mode_buttons_layout.addWidget(self.original_mode_button)
        self.mode_buttons_layout.addWidget(self.hedge_mode_button)

        self.layout_main.addWidget(self.mode_buttons_widget)

        # Stacked widget to hold different layouts for each mode
        self.stacked_widget = QStackedWidget()
        self.layout_main.addWidget(self.stacked_widget)

        # Add pages for each mode
        self.original_mode_widget = QWidget()
        self.original_mode_layout = QVBoxLayout(self.original_mode_widget)
        self.setup_original_mode_layout()
        self.stacked_widget.addWidget(self.original_mode_widget)

        self.hedge_mode_widget = QWidget()
        self.hedge_mode_layout = QVBoxLayout(self.hedge_mode_widget)
        self.setup_hedge_mode_layout()
        self.stacked_widget.addWidget(self.hedge_mode_widget)

        if self.current_mode == "Original Mode":
            self.original_mode_button.setChecked(True)
            self.stacked_widget.setCurrentWidget(self.original_mode_widget)
        else:
            self.hedge_mode_button.setChecked(True)
            self.stacked_widget.setCurrentWidget(self.hedge_mode_widget)

        self.confirm_button_widget = QWidget()
        self.confirm_button_layout = QHBoxLayout(self.confirm_button_widget)
        self.confirm_button = QPushButton("Confirm")
        self.cancel_button = QPushButton("Cancel")

        self.confirm_button.clicked.connect(self.confirm_button_clicked)
        self.cancel_button.clicked.connect(self.cancel_button_clicked)

        self.confirm_button_layout.addWidget(self.confirm_button)
        self.confirm_button_layout.addWidget(self.cancel_button)

        self.layout_main.addWidget(self.confirm_button_widget)

        self.central_widget.setLayout(self.layout_main)

    def cancel_button_clicked(self):
        self.close()

    def confirm_button_clicked(self):
        data = {}
        if self.current_mode == "Original Mode":
            data = { "leverage_main" : self.original_mode_spinBox.value(), "leverage_secondary" : None} 
        else:
            data = { "leverage_main" : self.hedge_mode_long_spinBox.value(), "leverage_secondary" : self.hedge_mode_short_spinBox.value()} 
        self.emitter_confirm_button_clicked.emit(data)

    def setup_original_mode_layout(self):
        self.original_mode_leverage_label = QLabel("Leverage")
        self.original_mode_slider = QSlider(Qt.Horizontal)
        self.original_mode_slider.setMinimum(1)
        self.original_mode_slider.setMaximum(self.max_leverage)
        self.original_mode_slider.setTickInterval(1)
        self.original_mode_slider.setSingleStep(1)
        self.original_mode_slider.setValue(int(self.leverage_main))
        self.original_mode_slider.valueChanged.connect(self.sliderValueChanged)

        self.original_mode_spinBox = QSpinBox()
        self.original_mode_spinBox.setMinimum(1)
        self.original_mode_spinBox.setMaximum(self.max_leverage)
        self.original_mode_spinBox.setSingleStep(1)
        self.original_mode_spinBox.setValue(int(self.leverage_main))
        self.original_mode_spinBox.valueChanged.connect(self.spinBoxValueChanged)

        self.original_mode_layout.addWidget(self.original_mode_leverage_label)
        self.original_mode_layout.addWidget(self.original_mode_slider)
        self.original_mode_layout.addWidget(self.original_mode_spinBox)

    def setup_hedge_mode_layout(self):
        self.hedge_mode_long_leverage_label = QLabel("Leverage (Long)")
        self.hedge_mode_short_leverage_label = QLabel("Leverage (Short)")

        self.hedge_mode_long_slider = QSlider(Qt.Horizontal)
        self.hedge_mode_long_slider.setMinimum(1)
        self.hedge_mode_long_slider.setMaximum(self.max_leverage)
        self.hedge_mode_long_slider.setTickInterval(1)
        self.hedge_mode_long_slider.setSingleStep(1)
        self.hedge_mode_long_slider.setValue(int(self.leverage_main))
        self.hedge_mode_long_slider.valueChanged.connect(self.sliderValueChanged)

        self.hedge_mode_short_slider = QSlider(Qt.Horizontal)
        self.hedge_mode_short_slider.setMinimum(1)
        self.hedge_mode_short_slider.setMaximum(self.max_leverage)
        self.hedge_mode_short_slider.setTickInterval(1)
        self.hedge_mode_short_slider.setSingleStep(1)

        if self.leverage_secondary:
            self.hedge_mode_short_slider.setValue(int(self.leverage_secondary))
        else:
            self.hedge_mode_short_slider.setValue(int(self.leverage_main))
        self.hedge_mode_short_slider.valueChanged.connect(self.sliderValueChanged)

        self.hedge_mode_long_spinBox = QSpinBox()
        self.hedge_mode_long_spinBox.setMinimum(1)
        self.hedge_mode_long_spinBox.setMaximum(self.max_leverage)
        self.hedge_mode_long_spinBox.setSingleStep(1)
        self.hedge_mode_long_spinBox.setValue(int(self.leverage_main))
        self.hedge_mode_long_spinBox.valueChanged.connect(self.spinBoxValueChanged)

        self.hedge_mode_short_spinBox = QSpinBox()
        self.hedge_mode_short_spinBox.setMinimum(1)
        self.hedge_mode_short_spinBox.setMaximum(self.max_leverage)
        self.hedge_mode_short_spinBox.setSingleStep(1)

        if self.leverage_secondary:
            self.hedge_mode_short_spinBox.setValue(int(self.leverage_secondary))
        else:
            self.hedge_mode_short_spinBox.setValue(int(self.leverage_main))
        self.hedge_mode_short_spinBox.valueChanged.connect(self.spinBoxValueChanged)

        self.hedge_mode_layout.addWidget(self.hedge_mode_long_leverage_label)
        self.hedge_mode_layout.addWidget(self.hedge_mode_long_spinBox)
        self.hedge_mode_layout.addWidget(self.hedge_mode_long_slider)

        self.hedge_mode_layout.addWidget(self.hedge_mode_short_leverage_label)
        self.hedge_mode_layout.addWidget(self.hedge_mode_short_spinBox)
        self.hedge_mode_layout.addWidget(self.hedge_mode_short_slider)

    def mode_button_clicked(self):
        button = self.sender()
        if button == self.original_mode_button:
            self.stacked_widget.setCurrentWidget(self.original_mode_widget)
            self.current_mode = "Original Mode"
            self.hedge_mode_button.setChecked(False)
            self.original_mode_button.setChecked(True)
        elif button == self.hedge_mode_button:
            self.stacked_widget.setCurrentWidget(self.hedge_mode_widget)
            self.current_mode = "Hedge Mode"
            self.original_mode_button.setChecked(False)
            self.hedge_mode_button.setChecked(True)

    def sliderValueChanged(self, value):
        sender = self.sender()
        if sender == self.original_mode_slider:
            self.original_mode_spinBox.setValue(value)
        elif sender == self.hedge_mode_long_slider:
            self.hedge_mode_long_spinBox.setValue(value)
        elif sender == self.hedge_mode_short_slider:
            self.hedge_mode_short_spinBox.setValue(value)

    def spinBoxValueChanged(self, value):
        sender = self.sender()
        if sender == self.original_mode_spinBox:
            self.original_mode_slider.setValue(value)
        elif sender == self.hedge_mode_long_spinBox:
            self.hedge_mode_long_slider.setValue(value)
        elif sender == self.hedge_mode_short_spinBox:
            self.hedge_mode_short_slider.setValue(value)

    def setup_css(self):
        self.central_widget.setStyleSheet("background-color: #101014;")

        self.trading_settings_label.setStyleSheet("color: #a8a8a8; font-size: 20px; font-weight: bold; ")

        self.original_mode_button.setFixedWidth(250)
        self.hedge_mode_button.setFixedWidth(250)
        self.confirm_button.setFixedWidth(130)
        self.cancel_button.setFixedWidth(130)

        self.confirm_button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.original_mode_button.setStyleSheet("""
            QPushButton { background-color: #08080a; border: 2px solid #a8a8a8; color: #a8a8a8; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 5px; padding: 5px;}
            QPushButton:checked { background-color: #101014; border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 5px; padding: 5px;}
        """)

        self.hedge_mode_button.setStyleSheet("""
            QPushButton { background-color: #08080a; border: 2px solid #a8a8a8; color: #a8a8a8; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 5px; padding: 5px;}
            QPushButton:checked { background-color: #101014; border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 5px; padding: 5px;}
        """)

        self.confirm_button.setStyleSheet("""
            QPushButton { background-color: #08080a; border: 2px solid #a8a8a8; color: #a8a8a8; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 5px; padding: 5px;}
            QPushButton:clicked { background-color: #101014; border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 5px; padding: 5px;}
        """)

        self.cancel_button.setStyleSheet("""
            QPushButton { background-color: #08080a; border: 2px solid #a8a8a8; color: #a8a8a8; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 5px; padding: 5px;}
            QPushButton:clicked { background-color: #101014; border: 2px solid #ffa200; color: #ffa200; font-family: BinancePlex, Arial; font-size: 14px; border-radius: 5px; padding: 5px;}
        """)

        self.original_mode_leverage_label.setStyleSheet("color: #a8a8a8; font-size: 14px; border: none")
        self.original_mode_leverage_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.original_mode_widget.setStyleSheet("background-color: #08080a; color: #a8a8a8; font-size: 12px; border: 1px solid #333333; border-radius: 5px; font-family: BinancePlex, Arial; margin-left: 5%; margin-right: 5%;")

        self.original_mode_slider.setFixedWidth(self.original_mode_widget.maximumWidth())
        self.original_mode_slider.setFixedHeight(50)
        self.original_mode_slider.setStyleSheet("""
            QSlider::groove:horizontal { background: #333333; border: 1px solid #333333; height: 10px; border-radius: 5px;}
            QSlider::handle:horizontal { background: #ffa200; border: 1px solid #ffa200; width: 10px; margin: -5px 0; border-radius: 5px;}
        """)
        self.original_mode_widget.setFixedHeight(150)
        self.original_mode_spinBox.setFixedWidth(self.original_mode_widget.maximumWidth())
        self.original_mode_spinBox.setFixedHeight(50)
        self.original_mode_spinBox.setStyleSheet("""
            QSpinBox { color: #ffa200; font-size: 14px; margin-bottom: 10%;}
        """)

        self.hedge_mode_long_leverage_label.setStyleSheet("color: #a8a8a8; font-size: 14px; border: none")
        self.hedge_mode_short_leverage_label.setStyleSheet("color: #a8a8a8; font-size: 14px; border: none")

        self.hedge_mode_long_leverage_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.hedge_mode_short_leverage_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.hedge_mode_widget.setStyleSheet("background-color: #08080a; color: #a8a8a8; font-size: 12px; border: 1px solid #333333; border-radius: 5px; font-family: BinancePlex, Arial; margin-left: 5%; margin-right: 5%;")

        self.hedge_mode_long_slider.setFixedWidth(self.original_mode_widget.maximumWidth())
        self.hedge_mode_short_slider.setFixedWidth(self.original_mode_widget.maximumWidth())

        self.hedge_mode_long_slider.setFixedHeight(50)
        self.hedge_mode_short_slider.setFixedHeight(50)

        self.hedge_mode_long_slider.setStyleSheet("""
            QSlider::groove:horizontal { background: #333333; border: 1px solid #333333; height: 10px; border-radius: 5px;}
            QSlider::handle:horizontal { background: #ffa200; border: 1px solid #ffa200; width: 10px; margin: -5px 0; border-radius: 5px;}
        """)
        self.hedge_mode_short_slider.setStyleSheet("""
            QSlider::groove:horizontal { background: #333333; border: 1px solid #333333; height: 10px; border-radius: 5px;}
            QSlider::handle:horizontal { background: #ffa200; border: 1px solid #ffa200; width: 10px; margin: -5px 0; border-radius: 5px;}
        """)

        self.hedge_mode_widget.setFixedHeight(300)

        self.hedge_mode_long_spinBox.setFixedWidth(self.original_mode_widget.maximumWidth())
        self.hedge_mode_short_spinBox.setFixedWidth(self.original_mode_widget.maximumWidth())
        self.hedge_mode_long_spinBox.setFixedHeight(50)
        self.hedge_mode_short_spinBox.setFixedHeight(50)
        self.hedge_mode_long_spinBox.setStyleSheet("""QSpinBox { color: #ffa200; font-size: 14px; margin-bottom: 10%;}""")
        self.hedge_mode_short_spinBox.setStyleSheet("""QSpinBox { color: #ffa200; font-size: 14px; margin-bottom: 10%;}""")
