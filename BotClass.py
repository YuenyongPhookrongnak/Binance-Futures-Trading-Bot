from ta.momentum import stochrsi_d, stochrsi_k, stoch, stoch_signal, rsi
from ta.trend import ema_indicator, macd_signal, macd, sma_indicator
from ta.volatility import average_true_range, bollinger_pband
import pandas as pd
import TradingStrats as TS
from Logger import *
from LiveTradingConfig import custom_tp_sl_functions, make_decision_options, wait_for_candle_close
import sys
import os
from typing import List, Optional, Any  # เพิ่ม imports สำหรับ type hints


class Bot:
    def __init__(self, symbol: str, Open: List[float], Close: List[float], High: List[float], 
                 Low: List[float], Volume: List[float], Date: List[str], OP: int, CP: int, 
                 index: int, tick: float, strategy: str, TP_SL_choice: str, SL_mult: float, 
                 TP_mult: float, backtesting: int = 0, signal_queue: Optional[Any] = None, 
                 print_trades_q: Optional[Any] = None):
        self.symbol = symbol
        self.Date = Date

        # Remove extra candle if present
        shortest = min(len(Open), len(Close), len(High), len(Low), len(Volume))
        self.Open = Open[-shortest:]
        self.Close = Close[-shortest:]
        self.High = High[-shortest:]
        self.Low = Low[-shortest:]
        self.Volume = Volume[-shortest:]

        self.OP = OP
        self.CP = CP
        self.index = index
        self.add_hist_complete = 0
        self.Open_H: List[float] = []
        self.Close_H: List[float] = []
        self.High_H: List[float] = []
        self.Low_H: List[float] = []
        self.tick_size = tick
        self.socket_failed = False
        self.backtesting = backtesting
        self.use_close_pos = False
        self.strategy = strategy
        self.TP_SL_choice = TP_SL_choice
        self.SL_mult = SL_mult
        self.TP_mult = TP_mult
        self.indicators = {}
        self.current_index = -1  ## -1 for live Bot to always reference the most recent candle, will update in Backtester
        self.take_profit_val: List[float] = []
        self.stop_loss_val: List[float] = []
        self.peaks: List[float] = []
        self.troughs: List[float] = []
        self.signal_queue = signal_queue
        
        # GPT Strategy specific attributes
        self.last_gpt_analysis: Optional[Any] = None
        self.gpt_confidence_score: float = 0
        self.market_structure: dict = {}
        
        # Websocket attributes
        self.stream: Optional[Any] = None  # เพิ่ม attribute สำหรับ websocket stream
        self.first_interval: bool = False
        self.pop_previous_value: bool = False
        
        if self.index == 0:
            self.print_trades_q = print_trades_q
        if backtesting:
            self.add_hist([], [], [], [], [], [])
            self.update_indicators()
            self.update_TP_SL()

    def update_indicators(self) -> None:
        """
        อัพเดท indicators - เน้นเฉพาะตัวที่ GPT strategy ใช้
        """
        try:
            # สำหรับ GPT Strategy ใช้ indicators พื้นฐาน
            if self.strategy == 'GPT_Market_Analysis':
                CloseS = pd.Series(self.Close)
                HighS = pd.Series(self.High)
                LowS = pd.Series(self.Low)
                VolumeS = pd.Series(self.Volume)
                
                self.indicators = {
                    "EMA_20": {"values": list(ema_indicator(CloseS, window=20)),
                              "plotting_axis": 1},
                    "EMA_50": {"values": list(ema_indicator(CloseS, window=50)),
                              "plotting_axis": 1},
                    "EMA_200": {"values": list(ema_indicator(CloseS, window=200)),
                               "plotting_axis": 1},
                    "RSI": {"values": list(rsi(CloseS)),
                           "plotting_axis": 3},
                    "Volume": {"values": list(VolumeS),
                              "plotting_axis": 2}
                }
            else:
                # Keep legacy strategies for backward compatibility
                self._update_legacy_indicators()
                
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            log.error(f'update_indicators() - Error occurred with strategy: {self.strategy}, Error Info: {exc_obj, fname, exc_tb.tb_lineno}, Error: {e}')

    def _update_legacy_indicators(self) -> None:
        """
        Legacy indicators สำหรับ backward compatibility
        """
        CloseS = pd.Series(self.Close)
        HighS = pd.Series(self.High)
        LowS = pd.Series(self.Low)
        
        match self.strategy:
            case 'StochRSIMACD':
                self.indicators = {"fastd": {"values": list(stoch(close=CloseS, high=HighS, low=LowS)),
                                             "plotting_axis": 3},
                                   "fastk": {"values": list(stoch_signal(close=CloseS, high=HighS, low=LowS)),
                                             "plotting_axis": 3},
                                   "RSI": {"values": list(rsi(CloseS)),
                                           "plotting_axis": 4},
                                   "MACD": {"values": list(macd(CloseS)),
                                            "plotting_axis": 5},
                                   "macdsignal": {"values": list(macd_signal(CloseS)),
                                                  "plotting_axis": 5}
                }
            case 'tripleEMAStochasticRSIATR':
                self.indicators = { "EMA_L": {"values": list(ema_indicator(CloseS, window=100)),
                                              "plotting_axis": 1},
                                    "EMA_M": {"values": list(ema_indicator(CloseS, window=50)),
                                              "plotting_axis": 1},
                                    "EMA_S": {"values": list(ema_indicator(CloseS, window=20)),
                                              "plotting_axis": 1},
                                    "fastd": {"values": list(stochrsi_d(CloseS)),
                                              "plotting_axis": 3},
                                    "fastk": {"values": list(stochrsi_k(CloseS)),
                                              "plotting_axis": 3}
                }
            case _:
                # Default minimal indicators
                self.indicators = {"EMA_20": {"values": list(ema_indicator(CloseS, window=20)),
                                              "plotting_axis": 1},
                                   "RSI": {"values": list(rsi(CloseS)),
                                           "plotting_axis": 3}
                }

    def handle_socket_message(self, msg: dict) -> None:
        """
        Handle incoming websocket messages from Binance
        """
        try:
            if msg['e'] == 'kline':
                kline = msg['k']
                
                # Check if candle is closed
                is_closed = kline['x']
                
                # Extract OHLCV data
                open_price = float(kline['o'])
                high_price = float(kline['h'])
                low_price = float(kline['l'])
                close_price = float(kline['c'])
                volume = float(kline['v'])
                close_time = int(kline['T'])
                
                if is_closed:
                    # Add completed candle to history
                    self.Open.append(open_price)
                    self.High.append(high_price)
                    self.Low.append(low_price)
                    self.Close.append(close_price)
                    self.Volume.append(volume)
                    self.Date.append(close_time)
                    
                    # Limit data size to prevent memory issues
                    max_candles = 1000
                    if len(self.Close) > max_candles:
                        self.Open = self.Open[-max_candles:]
                        self.High = self.High[-max_candles:]
                        self.Low = self.Low[-max_candles:]
                        self.Close = self.Close[-max_candles:]
                        self.Volume = self.Volume[-max_candles:]
                        self.Date = self.Date[-max_candles:]
                    
                    # Update indicators with new data
                    self.update_indicators()
                    
                    # Update TP/SL if needed
                    self.update_TP_SL()
                    
                    # For GPT strategy, trigger analysis
                    if self.strategy == 'GPT_Market_Analysis':
                        log.info(f"New candle completed for {self.symbol} - Price: {close_price}")
                        # Signal for GPT analysis could be added here
                        if self.signal_queue:
                            self.signal_queue.put({
                                'type': 'new_candle',
                                'symbol': self.symbol,
                                'price': close_price,
                                'timestamp': close_time
                            })
                    
                    log.debug(f"Candle updated for {self.symbol}: O:{open_price} H:{high_price} L:{low_price} C:{close_price} V:{volume}")
                else:
                    # Update current candle (live data)
                    if len(self.Close) > 0:
                        # Update the last candle with current data
                        self.Open[-1] = open_price
                        self.High[-1] = high_price  
                        self.Low[-1] = low_price
                        self.Close[-1] = close_price
                        self.Volume[-1] = volume
                        
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            log.error(f'handle_socket_message() - Error for {self.symbol}, Error Info: {exc_obj, fname, exc_tb.tb_lineno}, Error: {e}')
            self.socket_failed = True

    def add_hist(self, Date_temp: List[int], Open_temp: List[float], Close_temp: List[float], 
                 High_temp: List[float], Low_temp: List[float], Volume_temp: List[float]) -> None:
        """
        Add historical data to the bot
        """
        try:
            # Extend existing data with historical data
            self.Date.extend(Date_temp)
            self.Open.extend(Open_temp)
            self.Close.extend(Close_temp)
            self.High.extend(High_temp)
            self.Low.extend(Low_temp)
            self.Volume.extend(Volume_temp)
            
            # Update indicators after adding historical data
            self.update_indicators()
            
            log.info(f"Historical data added for {self.symbol}: {len(Date_temp)} candles")
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            log.error(f'add_hist() - Error for {self.symbol}, Error Info: {exc_obj, fname, exc_tb.tb_lineno}, Error: {e}')

    def update_TP_SL(self) -> None:
        """
        Update Take Profit and Stop Loss values based on strategy
        """
        try:
            if self.strategy == 'GPT_Market_Analysis' and len(self.Close) > 0:
                # For GPT strategy, use dynamic TP/SL based on volatility
                current_price = self.Close[-1]
                
                # Calculate ATR for dynamic TP/SL
                if len(self.Close) >= 14:
                    high_series = pd.Series(self.High)
                    low_series = pd.Series(self.Low)
                    close_series = pd.Series(self.Close)
                    
                    atr_values = average_true_range(high_series, low_series, close_series, window=14)
                    current_atr = atr_values.iloc[-1] if not pd.isna(atr_values.iloc[-1]) else current_price * 0.02
                    
                    # Dynamic TP/SL based on ATR
                    stop_loss = current_atr * self.SL_mult
                    take_profit = current_atr * self.TP_mult
                    
                    self.stop_loss_val = [stop_loss]
                    self.take_profit_val = [take_profit]
                    
                    log.debug(f"TP/SL updated for {self.symbol}: SL={stop_loss:.6f}, TP={take_profit:.6f}, ATR={current_atr:.6f}")
                    
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            log.error(f'update_TP_SL() - Error for {self.symbol}, Error Info: {exc_obj, fname, exc_tb.tb_lineno}, Error: {e}')