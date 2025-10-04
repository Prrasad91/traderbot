import pandas as pd
import numpy as np
from datetime import datetime
from tradingview_ta import TA_Handler, Interval
import websocket
import json
from .. import config

class MarketDataCollector:
    def __init__(self):
        self.handlers = {
            "5m": TA_Handler(
                symbol=config.SYMBOL,
                exchange=config.EXCHANGE,
                screener=config.SCREENER,
                interval=Interval.INTERVAL_5_MINUTES
            ),
            "15m": TA_Handler(
                symbol=config.SYMBOL,
                exchange=config.EXCHANGE,
                screener=config.SCREENER,
                interval=Interval.INTERVAL_15_MINUTES
            ),
            "1h": TA_Handler(
                symbol=config.SYMBOL,
                exchange=config.EXCHANGE,
                screener=config.SCREENER,
                interval=Interval.INTERVAL_1_HOUR
            )
        }
    
    def get_nifty_data(self):
        try:
            all_data = {}
            
            for interval, handler in self.handlers.items():
                analysis = handler.get_analysis()
                indicators = analysis.indicators
                
                data = pd.DataFrame({
                    'Timestamp': [pd.Timestamp.now()],
                    'Open': [indicators['open']],
                    'High': [indicators['high']],
                    'Low': [indicators['low']],
                    'Close': [indicators['close']],
                    'Volume': [indicators['volume']],
                    'RSI': [indicators.get('RSI', 0)],
                    'ADX': [indicators.get('ADX', 0)],
                    'ATR': [indicators.get('ATR', 0)],
                    'MACD': [indicators.get('MACD.macd', 0)],
                    'MACD_Signal': [indicators.get('MACD.signal', 0)],
                    'BB_Upper': [indicators.get('BB.upper', 0)],
                    'BB_Middle': [indicators.get('BB.middle', 0)],
                    'BB_Lower': [indicators.get('BB.lower', 0)]
                })
                
                all_data[interval] = {
                    'data': data,
                    'summary': analysis.summary,
                    'moving_averages': analysis.moving_averages,
                    'oscillators': analysis.oscillators
                }
            
            return all_data
            
        except Exception as e:
            print(f"Error fetching Nifty data: {str(e)}")
            return None
    
    def get_institutional_data(self):
        # Simulated institutional data
        return {
            'FII': {'buy': 1000, 'sell': 800},
            'DII': {'buy': 900, 'sell': 1100}
        }
    
    def get_option_chain(self):
        # Simulated option chain data
        return {
            'ATM': 19500,
            'PCR': 0.85,
            'max_pain': 19400
        }
    
    def get_global_indices(self):
        # Simulated global indices data
        return {
            'DOW': {'change': 0.5},
            'NASDAQ': {'change': -0.2},
            'FTSE': {'change': 0.3}
        }
