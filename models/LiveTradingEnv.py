import gym
from gym import spaces
import numpy as np
import stable_baselines3
from stable_baselines3 import PPO
import random
import pandas as pd
import matplotlib.pyplot as plt

class LiveTradingEnv(gym.Env):

    def __init__(self, df, accountBalance,riskToReward, accountRiskPercentage):
        super(LiveTradingEnv, self).__init__()
        
        self.long_gaps = []
        self.short_gaps = []
        self.long_Gaps_Checked_Until = 0
        self.short_Gaps_Checked_Until = 0
        #Environment Variables
        self.df = df  # DataFrame containing market data
        self.action_space = spaces.Discrete(3) #(buy, sell, hold)

        #Active Trade Variables
        self.position = None  # 'long', 'short', or None
        self.tp = None  # Take Profit level
        self.sl = None  # Stop Loss level
        self.accountBalance = accountBalance
        self.leverageToUse = 10
        self.entry_price = 0
        self.trade_fee = 0
        self.fee_rate = 0.00055*2
        self.tradeValue = 0
        self.tradeQuantity = 0
        self.riskToRewardRatio = riskToReward
        self.accountRiskPercentage = accountRiskPercentage 

        self.long_gaps = []
        self.short_gaps = []
        self.long_Gaps_Checked_Until = 0
        self.short_Gaps_Checked_Until = 0

        #Evaluation Variables
        self.overTimeWinnings = []
        self.lossesToWinsLog = []
        self.executedTrades = []
        self.currentTrade = {}
        self.episode_reward = 0
        self.total_trades = 0
        self.total_wins = 0
        self.total_losses = 0
        self.lossesToWins = 0

        self.current_step = 100
        # Define observation space (using the shape of the market data)
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(len(df.columns),), dtype=np.float32)


    def reset(self):
        if self.currentTrade != {}:
            self.executedTrades.append(self.currentTrade)
            self.currentTrade = {}
        #Reset Trade Related Variables
        self.trade_fee = 0
        self.tradeQuantity = 0
        self.entry_price = 0
        self.tp = None
        self.sl = None

        # Reset state and position tracking variables
        self.position = None
        self.episode_reward = 0
        # self.current_step = 100

        #Progress Tracking Variables
        self.overTimeWinnings.append(self.accountBalance)
        self.lossesToWinsLog.append(self.lossesToWins)
        return self.df.iloc[self.current_step].values.astype(np.float32)

    def calculate_reward(self, entry_price, current_price, position):
        if position == 'Long':
            tradeResult = (current_price - entry_price)*self.tradeQuantity - self.trade_fee
            print("Trade Fee is:",self.trade_fee)
            self.accountBalance += tradeResult
            print('Trade Type: ', position, ' resulted in: ', tradeResult, ' Making the account balance: ', self.accountBalance)
            return tradeResult  # Profit or loss for long position
        elif position == 'Short':
            tradeResult = (entry_price - current_price)*self.tradeQuantity - self.trade_fee
            print("Trade Fee is:",self.trade_fee)
            self.accountBalance += tradeResult
            print('Trade Type: ', position, ' resulted in: ', tradeResult, ' Making the account balance: ', self.accountBalance)
            return tradeResult  # Profit or loss for short position

    def step(self, action):
        # Get the current price from the dataframe (you might use 'close_price')
        current_price_high = self.df.iloc[self.current_step]['high_price']
        current_price_low = self.df.iloc[self.current_step]['low_price']
        candle_open_time = pd.to_datetime(self.df.iloc[self.current_step]['open_time'], unit='ms')
        reward = 0
        done = False
        info = {}
        self.add_new_gaps()

        entered_trade = False
        closed_trade = False

        # if action != 0:
            # print("Action:",action)
        # If there's no open position, check if the agent wants to open one
        is_gap, gap = self.if_current_candle_in_gap()
        
        if self.position is None:
            if action == 1 and is_gap == 1:  # Buy
                self.long_gaps.remove(gap)
                self.total_trades +=1
                self.position = 'Long'
                ##Old
                # self.entry_price = avg_price
                # self.tradeValue = self.leverageToUse * self.accountBalance
                # self.tradeQuantity = self.tradeValue / self.entry_price
                # self.trade_fee = self.tradeValue * self.fee_rate

                # # Define your TP and SL based on your strategy
                # self.tp = self.entry_price * 1.012
                # self.sl = self.entry_price * 0.994

                #New
                self.entry_price = gap['entry_price']
                self.sl = float(gap['stop_loss'])
                stop_loss_in_perc = 1 - self.sl/self.entry_price
                
                money_risk = self.accountBalance * self.accountRiskPercentage
                self.tradeValue = money_risk / stop_loss_in_perc

                tp_in_perc = stop_loss_in_perc * self.riskToRewardRatio
                self.tp = self.entry_price * (1 + tp_in_perc)

                self.tradeQuantity = self.tradeValue / self.entry_price
                self.trade_fee = self.tradeValue * self.fee_rate
                print("Trade Fee is:", self.trade_fee)
                # Define your TP and SL based on your strategy

                self.currentTrade = { "Position Type" : self.position,
                                    "Entry Price" : self.entry_price,
                                    "Trade total Value" : self.tradeValue,
                                    "Quantity" : self.tradeQuantity,
                                    "Take Profit" : self.tp,
                                    "Stop Loss" : self.sl,
                                    "Entry Time" : candle_open_time
                                    }
                info['Current Trade'] = self.currentTrade
                entered_trade = True
                print("Entering a Long Trade at - ", self.entry_price)

            elif action == 2 and is_gap == 2:  # Sell/Short
                self.short_gaps.remove(gap)
                self.total_trades +=1
                self.position = 'Short'

                ##Old
                # self.entry_price = avg_price
                # self.tradeValue = self.leverageToUse * self.accountBalance
                # self.tradeQuantity = self.tradeValue / self.entry_price
                # self.trade_fee = self.tradeValue * self.fee_rate

                # # Define your TP and SL based on your strategy
                # self.tp = self.entry_price * 0.988
                # self.sl = self.entry_price * 1.006

                self.entry_price = gap['entry_price']
                self.sl = float(gap['stop_loss'])
                stop_loss_in_perc = 1 - (self.entry_price/ self.sl)
                money_risk = self.accountBalance * self.accountRiskPercentage
                self.tradeValue = money_risk / stop_loss_in_perc
                tp_in_perc = stop_loss_in_perc * self.riskToRewardRatio
                self.tp = self.entry_price * (1 - tp_in_perc)

                self.tradeQuantity = self.tradeValue / self.entry_price
                self.trade_fee = self.tradeValue * self.fee_rate
                print("Trade Fee is:", self.trade_fee)

                self.currentTrade = { "Position Type" : self.position,
                                    "Entry Price" : self.entry_price,
                                    "Trade total Value" : self.tradeValue,
                                    "Quantity" : self.tradeQuantity,
                                    "Take Profit" : self.tp,
                                    "Stop Loss" : self.sl,
                                    "Entry Time" : candle_open_time
                                    }
                entered_trade = True
                print("Entering a Short Trade Trade at - ", self.entry_price)

        # Check if the position should be closed (TP or SL hit)
        if self.position == 'Long':
            if current_price_high >= self.tp or current_price_low <= self.sl:
                random_number = random.random()
                close_price = 0

                if random_number >= 0.5:
                    if current_price_high >= self.tp:
                        close_price = self.tp
                    else:
                        close_price = self.sl
                else:
                    if current_price_low <= self.sl:
                        close_price = self.sl
                    else:
                        close_price = self.tp

                reward = self.calculate_reward(self.entry_price, close_price , self.position)

                if reward < 0:
                    self.total_losses += 1
                    self.lossesToWins -=1
                else:
                    self.total_wins +=1
                    self.lossesToWins +=1
                
                closed_trade = True
                print('Long Trade Closed')
                done = True
                self.episode_reward += reward
                self.position = None  # Reset position

        elif self.position == 'Short':
            #If Trade should be closed
            if current_price_low <= self.tp or current_price_high >= self.sl:
                random_number = random.random()
                close_price = 0

                #Since the candle low/high might hit both the TP and SP we simply make it 50/50 which one is checked first
                if random_number >= 0.5:
                    if current_price_high >= self.sl:
                        close_price = self.sl
                    else:
                        close_price = self.tp
                else:
                    if current_price_low <= self.tp:
                        close_price = self.tp
                    else:
                        close_price = self.sl

                reward = self.calculate_reward(self.entry_price, close_price , self.position)

                if reward < 0:
                    self.total_losses += 1
                    self.lossesToWins -=1
                else:
                    self.total_wins +=1
                    self.lossesToWins +=1

                closed_trade = True
                print('Short Trade Closed')
                done = True
                self.episode_reward += reward
                self.position = None  # Reset position


        self.current_step += 1

        info = { "Entered Trade" : entered_trade,
                        "Closed Trade" : closed_trade,
                        "Current Trade" : self.currentTrade}
        
        next_state = self.df.iloc[self.current_step % len(self.df)].values
        
        return next_state.astype(np.float32), reward, done, info

    def render(self, mode='human', close=False):
        # For example, print current step
        print(f"Current Step: {self.current_step}")

    def getTrades(self):
        return self.total_trades
    
    def getTotalWins(self):
        return self.total_wins
    
    def getTotalLosses(self):
        return self.total_losses
    
    def getWinnings(self):
        return self.accountBalance
    
    def add_new_gaps(self):
    # def add_new_gaps(self,current_step,df,long_gaps,short_gaps,long_Gaps_Checked_Until,short_Gaps_Checked_Until,):
    
        if self.current_step > self.long_Gaps_Checked_Until:
            new_long_gaps = self.calculate_long_gaps()
            for gap in new_long_gaps:
                self.long_gaps.append(gap)

        for gap in self.long_gaps:
            if self.current_step - int(gap['end']) > 2304:
                self.long_gaps.remove(gap)
            else:
                break

        if self.current_step > self.short_Gaps_Checked_Until:
            new_short_gaps = self.calculate_short_gaps()
            for gap in new_short_gaps:
                self.short_gaps.append(gap)

        for gap in self.short_gaps:
            if self.current_step - int(gap['end']) > 2304:
                self.short_gaps.remove(gap)
            else:
                break

    def setNewAccountBalance(self,currentBalance):
        self.accountBalance = currentBalance

    def calculate_long_gaps(self):
        gaps = []
        for self.long_Gaps_Checked_Until in range(self.long_Gaps_Checked_Until, self.current_step - 2):
            first_candle = self.df.iloc[self.long_Gaps_Checked_Until]
            third_candle = self.df.iloc[self.long_Gaps_Checked_Until + 2]

            if float(first_candle['high_price']) <= float(third_candle['low_price']):
                entry_price = (float(third_candle['low_price']) + float(first_candle['high_price'])) / 2
                stop_loss = float(first_candle['low_price'])
                stop_loss_in_perc = 1 - stop_loss/entry_price
                if(stop_loss_in_perc >= 0.002):
                    gap_info = {
                        'start': self.long_Gaps_Checked_Until,
                        'end': self.long_Gaps_Checked_Until + 2,
                        'time': first_candle['open_time'],
                        'high_price': third_candle['low_price'],
                        'low_price': first_candle['high_price'],
                        'entry_price': entry_price,
                        'stop_loss': first_candle['low_price'],
                        'stop_loss_in_perc': stop_loss_in_perc,
                        'filled': False
                        }
                    gaps.append(gap_info)
            else:
                for gap in gaps[::-1]:
                    if float(first_candle['low_price']) < float(gap['high_price']):
                        # Remove the gap from the list as it's no longer needed
                        gaps.remove(gap)

        self.long_Gaps_Checked_Until = self.current_step - 2
        return gaps  # Return the list of gaps for further use or analysis
    
    def calculate_short_gaps(self):
        gaps = []
        for self.short_Gaps_Checked_Until in range(self.short_Gaps_Checked_Until, self.current_step - 2):
            first_candle = self.df.iloc[self.short_Gaps_Checked_Until]
            third_candle = self.df.iloc[self.short_Gaps_Checked_Until + 2]

            if float(first_candle['low_price']) > float(third_candle['high_price']):
                entry_price = (float(first_candle['low_price']) + float(third_candle['high_price'])) / 2
                stop_loss = float(first_candle['high_price'])
                stop_loss_in_perc = 1 - entry_price/stop_loss
                if(stop_loss_in_perc >= 0.002):
                    gap_info = {
                        'start': self.short_Gaps_Checked_Until,
                        'end': self.short_Gaps_Checked_Until + 2,
                        'time': first_candle['open_time'],
                        'high_price': first_candle['low_price'],
                        'low_price': third_candle['high_price'],
                        'entry_price': entry_price,
                        'stop_loss': first_candle['high_price'],
                        'stop_loss_in_perc': stop_loss_in_perc,
                        'filled': False
                        }
                    gaps.append(gap_info)
            else:
                for gap in gaps[::-1]:
                    if float(first_candle['high_price'])> float(gap['low_price']) :
                        # Remove the gap from the list as it's no longer needed
                        gaps.remove(gap)
                        
        self.short_Gaps_Checked_Until = self.current_step - 2
        return gaps  # Return the list of gaps for further use or analysis
        

    def if_current_candle_in_gap(self):
        current_candle = self.df.iloc[self.current_step]

        for gap in self.long_gaps[::-1]:
            if current_candle['low_price'] <= gap['entry_price']:
                # self.long_gaps.remove(gap)
                return 1, gap
            
        for gap in self.short_gaps[::-1]:
            if current_candle['high_price'] >= gap['entry_price']:
                # self.short_gaps.remove(gap)
                return 2, gap

        return 0, []
         
    def render_all(self, mode='human'):
        # Plot Total Rewards per Episode
        plt.figure(figsize=(30, 10))

        # Plot Total Profit over Episodes
        plt.subplot(1, 3, 2)
        plt.title('Total Profit over Time')
        plt.plot(self.overTimeWinnings)
        plt.xlabel('Episode')
        plt.ylabel('Total Profit')

        # # Plot Number of Trades over Episodes
        plt.subplot(1, 3, 3)
        plt.title('Number of Trades over Time')
        plt.plot(self.lossesToWinsLog)
        plt.xlabel('Episode')
        plt.ylabel('Number of Trades')

        # plt.tight_layout()
        plt.show()
