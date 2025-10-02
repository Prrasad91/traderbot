import pandas as pd
import numpy as np
from datetime import datetime

class TechnicalAnalyzer:
    def __init__(self):
        pass
    
    def calculate_vwap(self, data):
        """Calculate VWAP (Volume Weighted Average Price)"""
        if data is None or data.empty:
            return data
            
        df = data.copy()
        df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
        df['VP'] = df['Typical_Price'] * df['Volume']
        df['Cumulative_VP'] = df['VP'].cumsum()
        df['Cumulative_Volume'] = df['Volume'].cumsum()
        df['VWAP'] = df['Cumulative_VP'] / df['Cumulative_Volume']
        return df
    
    def identify_trend(self, data, period=20):
        """Identify trend direction using moving averages"""
        if data is None or data.empty or len(data) < period:
            return "undefined"
            
        df = data.copy()
        if len(df) >= period:
            df['SMA'] = df['Close'].rolling(window=period).mean()
            current_price = df['Close'].iloc[-1]
            sma = df['SMA'].iloc[-1]
            
            if pd.isna(sma):
                return "undefined"
            elif current_price > sma:
                return "uptrend"
            elif current_price < sma:
                return "downtrend"
            
        return "sideways"
    
    def identify_key_levels(self, data):
        """Identify support and resistance levels"""
        if data is None or data.empty:
            return {
                'high': None,
                'low': None,
                'prev_close': None,
                'vwap': None
            }
            
        pivot = {
            'high': float(data['High'].max()),
            'low': float(data['Low'].min()),
            'prev_close': float(data['Prev Close'].iloc[-1]) if 'Prev Close' in data.columns else float(data['Close'].iloc[-1]),
            'vwap': float(data['VWAP'].iloc[-1]) if 'VWAP' in data.columns else None
        }
        return pivot
    
    def validate_momentum(self, data, period=14):
        """Calculate momentum indicators (RSI)"""
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        return {
            'rsi': current_rsi,
            'momentum': 'bullish' if current_rsi > 50 else 'bearish'
        }
    
    def identify_candlestick_pattern(self, data):
        """Identify basic candlestick patterns"""
        row = data.iloc[-1]
        body = abs(row['Close'] - row['Open'])
        upper_wick = row['High'] - max(row['Open'], row['Close'])
        lower_wick = min(row['Open'], row['Close']) - row['Low']
        
        # Simple pattern recognition
        if body < 0.2 * (row['High'] - row['Low']) and upper_wick > body and lower_wick > body:
            return "doji"
        elif row['Close'] > row['Open'] and upper_wick < 0.2 * body and lower_wick < 0.2 * body:
            return "bullish_marubozu"
        elif row['Close'] < row['Open'] and upper_wick < 0.2 * body and lower_wick < 0.2 * body:
            return "bearish_marubozu"
        else:
            return "no_specific_pattern"
