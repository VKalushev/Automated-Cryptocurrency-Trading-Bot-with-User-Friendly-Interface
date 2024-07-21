# Automated Cryptocurrency Trading System
## Overview
This project is an automated cryptocurrency trading system designed to execute trades and analyze market data using reinforcement learning. The system interacts with Bybit and MEXC exchanges via APIs to perform real-time trading and data acquisition.

## Features
* Cryptocurrency Exchanges: Supports Bybit and MEXC exchanges for low trading fees and reliable APIs.
* Data Acquisition: Utilizes live and historical data from exchanges to inform trading decisions without storing data.
* Reinforcement Learning Model: Employs the PPO algorithm with an MlpPolicy to adapt to market changes, trained on BTCUSDT data from March 2020.
* User Interface: Provides a user-friendly interface with:
  * Registration and login functionality
  * Real-time candlestick graphs
  * User settings for email, password, API keys, and bot preferences
  * Display panels for wallet balance, trade history, and active positions
* Algorithm Execution: Real-time trading decisions based on live data using the trained model.
* Demo Accounts: Allows users to create demo accounts for testing without the need for API keys.

## Testing
* User-Interface Unit Testing: Ensures all UI components function correctly, including account creation, login, trade execution, and settings adjustments.
* Model Testing: Validated the model on unseen data, achieving a 58.83% win rate, growing an initial $100 balance to $3621 across 498 trades.

## Future Work
* Enhance the model by incorporating multiple trading strategies and improving trade management during active trades.
* Develop a backtesting environment for strategy evaluation.

## Conclusion
The system successfully automates cryptocurrency trading, providing a robust platform for users to engage with the market using advanced machine learning techniques.

