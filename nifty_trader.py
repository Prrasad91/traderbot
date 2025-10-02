import pandas as pd
import numpy as np
import requests
import json
import os
import winsound
from datetime import datetime, timedelta
from time import sleep
from tradingview_ta import TA_Handler, Interval, Exchange
import websocket
from threading import Thread
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pywhatkit as pwk
import webbrowser
from urllib.parse import quote

# Constants
# Add your WhatsApp number here (with country code, e.g., +911234567890)
WHATSAPP_NUMBER = ""  # Add your number here
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'X-Requested-With': 'XMLHttpRequest'
}

BASE_URL = "https://www.nseindia.com"
NIFTY_QUOTE_URL = f"{BASE_URL}/api/equity-stockIndices?index=NIFTY%2050"
OPTION_CHAIN_API = f"{BASE_URL}/api/option-chain-indices?symbol=NIFTY"
FII_DII_URL = f"{BASE_URL}/api/marketStatus"
COOKIE_URL = f"{BASE_URL}/get-quotes/equity?symbol=NIFTY"

class NSESession:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.cookies = None
        self.last_request_time = None
        self.min_delay = 1
        # Additional headers that might help
        self.session.headers.update({
            'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'Host': 'www.nseindia.com',
            'Referer': 'https://www.nseindia.com'
        })

    def _update_cookies(self):
        try:
            # First get the main page to set initial cookies
            self.session.get(BASE_URL, timeout=10)
            sleep(1)  # Small delay
            
            # Then get the specific page for more cookies
            response = self.session.get(COOKIE_URL, timeout=10)
            if response.status_code == 200:
                self.cookies = self.session.cookies
                return True
            return False
        except Exception as e:
            print(f"Error updating cookies: {str(e)}")
            return False

    def _wait_between_requests(self):
        if self.last_request_time:
            elapsed = (datetime.now() - self.last_request_time).total_seconds()
            if elapsed < self.min_delay:
                sleep(self.min_delay - elapsed)
        self.last_request_time = datetime.now()

    def make_request(self, url, method="GET", params=None, data=None, max_retries=3):
        if not self.cookies:
            self._update_cookies()

        self._wait_between_requests()

        for attempt in range(max_retries):
            try:
                if method.upper() == "GET":
                    response = self.session.get(
                        url,
                        params=params,
                        cookies=self.cookies,
                        timeout=10
                    )
                else:
                    response = self.session.post(
                        url,
                        params=params,
                        data=data,
                        cookies=self.cookies,
                        timeout=10
                    )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code in [401, 403]:
                    self._update_cookies()
                    continue
                else:
                    print(f"Request failed with status code: {response.status_code}")
                    
            except Exception as e:
                print(f"Request attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    sleep(2 ** attempt)
                    self._update_cookies()
                continue

        return None

class TradingViewSession:
    def __init__(self):
        self.ws = None
        self.last_data = None
        self.is_connected = False
        self.handler = TA_Handler(
            symbol="NIFTY",
            exchange="NSE",
            screener="india",
            interval=Interval.INTERVAL_5_MINUTES,
            timeout=30
        )
        # Create handlers for different timeframes
        self.handlers = {
            "5m": self.handler,
            "15m": TA_Handler(
                symbol="NIFTY",
                exchange="NSE",
                screener="india",
                interval=Interval.INTERVAL_15_MINUTES,
                timeout=30
            ),
            "1h": TA_Handler(
                symbol="NIFTY",
                exchange="NSE",
                screener="india",
                interval=Interval.INTERVAL_1_HOUR,
                timeout=30
            )
        }

    def connect(self):
        try:
            self.handler.get_analysis()
            return True
        except Exception as e:
            print(f"Error connecting to TradingView: {str(e)}")
            return False

    def get_analysis(self):
        try:
            data = {}
            for timeframe, handler in self.handlers.items():
                try:
                    analysis = handler.get_analysis()
                    indicators = analysis.indicators
                    oscillators = analysis.oscillators
                    moving_averages = analysis.moving_averages
                    
                    data[timeframe] = {
                        # Price data
                        'close': indicators.get('close', 0),
                        'open': indicators.get('open', 0),
                        'high': indicators.get('high', 0),
                        'low': indicators.get('low', 0),
                        'volume': indicators.get('volume', 0),
                        
                        # Technical indicators
                        'RSI': indicators.get('RSI', 0),
                        'RSI[1]': indicators.get('RSI[1]', 0),
                        'EMA20': indicators.get('EMA20', 0),
                        'EMA50': indicators.get('EMA50', 0),
                        'EMA200': indicators.get('EMA200', 0),
                        'SMA20': indicators.get('SMA20', 0),
                        'SMA50': indicators.get('SMA50', 0),
                        'SMA200': indicators.get('SMA200', 0),
                        
                        # Bollinger Bands
                        'BB.upper': indicators.get('BB.upper', 0),
                        'BB.lower': indicators.get('BB.lower', 0),
                        'BB.middle': indicators.get('BB.middle', 0),
                        
                        # MACD
                        'MACD.macd': indicators.get('MACD.macd', 0),
                        'MACD.signal': indicators.get('MACD.signal', 0),
                        
                        # Volume indicators
                        'ADX': indicators.get('ADX', 0),
                        'ADX+': indicators.get('ADX+DI', 0),
                        'ADX-': indicators.get('ADX-DI', 0),
                        
                        # Additional data
                        'Stoch.K': indicators.get('Stoch.K', 0),
                        'Stoch.D': indicators.get('Stoch.D', 0),
                        'ATR': indicators.get('ATR', 0),
                        
                        # Summary
                        'recommendation': analysis.summary.get('RECOMMENDATION', 'NEUTRAL'),
                        'oscillator_summary': oscillators.get('RECOMMENDATION', 'NEUTRAL'),
                        'ma_summary': moving_averages.get('RECOMMENDATION', 'NEUTRAL')
                    }
                except Exception as e:
                    print(f"Error getting {timeframe} analysis: {str(e)}")
                    continue
            
            return data
        except Exception as e:
            print(f"Error getting TradingView analysis: {str(e)}")
            return None

class TradingSystem:
    def __init__(self):
        self.tv_session = TradingViewSession()
        self.last_data = None
        self.risk_per_trade = 0.01  # 1% risk per trade
        self.min_rr_ratio = 1.5  # Minimum risk-reward ratio
        self.whatsapp_number = WHATSAPP_NUMBER
        
    def send_whatsapp_message(self, message):
        """Send a WhatsApp message using web.whatsapp.com"""
        try:
            if not self.whatsapp_number:
                print("Please set your WhatsApp number in the WHATSAPP_NUMBER constant")
                return False
                
            # Open WhatsApp Web with the message
            message_encoded = quote(message)
            url = f"https://web.whatsapp.com/send?phone={self.whatsapp_number}&text={message_encoded}"
            webbrowser.open(url)
            return True
        except Exception as e:
            print(f"Error sending WhatsApp message: {str(e)}")
            return False
            
    def format_trade_alert(self, bias, current_price, entry, stop_loss, target, analysis, indicators):
        """Format trade alert message for WhatsApp"""
        stars = "⭐" * int(analysis['strength'])
        message = f"""🚨 NIFTY TRADE ALERT 🚨
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Signal: {'🟢 BULLISH' if bias == 'bullish' else '🔴 BEARISH'}
Strength: {stars}
Current Price: ₹{current_price:.2f}

Setup:
{'🔼' if bias == 'bullish' else '🔽'} Entry: {'Above' if bias == 'bullish' else 'Below'} ₹{entry:.2f}
🛑 Stop Loss: {'Below' if bias == 'bullish' else 'Above'} ₹{stop_loss:.2f}
🎯 Target: ₹{target:.2f}

Key Indicators:
📊 RSI: {indicators['RSI']:.2f}
📈 ADX: {indicators['ADX']:.2f}

Top Reasons:"""
        
        # Add top 3 reasons
        for reason in analysis['reasons'][:3]:
            message += f"\n✅ {reason}"
            
        return message

    def get_nifty_data(self):
        """Get Nifty data - real or simulated"""
        if self.use_real_data:
            try:
                # Try multiple times with increasing delays
                for attempt in range(3):
                    try:
                        print(f"Attempt {attempt + 1} to fetch real data...")
                        response = self.nse_session.make_request(NIFTY_QUOTE_URL)
                        if response and isinstance(response, dict):
                            data = response.get('data', [{}])[0]
                            df = pd.DataFrame([{
                                'Open': float(data.get('open', 0)),
                                'High': float(data.get('dayHigh', 0)),
                                'Low': float(data.get('dayLow', 0)),
                                'Close': float(data.get('lastPrice', 0)),
                                'Volume': int(data.get('totalTradedVolume', 0)),
                                'Prev Close': float(data.get('previousClose', 0))
                            }], index=[pd.Timestamp.now()])
                            
                            print("Successfully fetched real data!")
                            self.last_nifty_data = df
                            return df
                    except Exception as inner_e:
                        print(f"Attempt {attempt + 1} failed: {str(inner_e)}")
                        sleep(2 ** attempt)  # Exponential backoff
                        continue
                    
                print("All attempts to fetch real data failed")
                print("Falling back to simulated data...")
            except Exception as e:
                print(f"Error in get_nifty_data: {str(e)}")
                print("Falling back to simulated data...")

        # Simulated data
        if self.last_nifty_data is not None:
            last_close = self.last_nifty_data['Close'].iloc[-1]
        else:
            last_close = 19500

        change = np.random.normal(0, 20)
        new_close = last_close + change
        high = max(new_close + abs(np.random.normal(0, 10)), new_close)
        low = min(new_close - abs(np.random.normal(0, 10)), new_close)
        
        df = pd.DataFrame({
            'Open': [last_close],
            'High': [high],
            'Low': [low],
            'Close': [new_close],
            'Volume': [int(np.random.normal(1000000, 100000))],
            'Prev Close': [last_close]
        }, index=[pd.Timestamp.now()])
        
        self.last_nifty_data = df
        return df

    def calculate_vwap(self, data):
        df = data.copy()
        df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
        df['VP'] = df['Typical_Price'] * df['Volume']
        df['Cumulative_VP'] = df['VP'].cumsum()
        df['Cumulative_Volume'] = df['Volume'].cumsum()
        df['VWAP'] = df['Cumulative_VP'] / df['Cumulative_Volume']
        return df

    def analyze_indicators(self, tv_data):
        """Analyze all indicators across timeframes to determine bias"""
        if not tv_data or '5m' not in tv_data:
            return None
        
        score = 0
        reasons = []
        trend_strength = 0
        current_price = tv_data['5m']['close']

        # Analyze each timeframe
        timeframes = ['5m', '15m', '1h']
        weights = {'5m': 0.5, '15m': 0.3, '1h': 0.2}  # Weight by importance
        
        for tf in timeframes:
            if tf not in tv_data:
                continue
                
            data = tv_data[tf]
            tf_score = 0
            tf_reasons = []

            # Trend Analysis using EMAs
            if current_price > data['EMA20'] > data['EMA50']:
                tf_score += 1
                tf_reasons.append(f"{tf} Uptrend (Price > EMA20 > EMA50)")
            elif current_price < data['EMA20'] < data['EMA50']:
                tf_score -= 1
                tf_reasons.append(f"{tf} Downtrend (Price < EMA20 < EMA50)")

            # RSI Analysis with momentum
            rsi = data['RSI']
            rsi_prev = data['RSI[1]']
            if rsi > 60 and rsi > rsi_prev:
                tf_score += 1
                tf_reasons.append(f"{tf} Strong RSI with momentum ({rsi:.2f})")
            elif rsi < 40 and rsi < rsi_prev:
                tf_score -= 1
                tf_reasons.append(f"{tf} Weak RSI with momentum ({rsi:.2f})")

            # MACD Analysis
            if data['MACD.macd'] > data['MACD.signal']:
                tf_score += 1
                tf_reasons.append(f"{tf} MACD bullish")
            else:
                tf_score -= 1
                tf_reasons.append(f"{tf} MACD bearish")

            # Bollinger Bands Analysis
            bb_pos = (current_price - data['BB.lower']) / (data['BB.upper'] - data['BB.lower'])
            if bb_pos > 0.8:
                tf_score -= 0.5
                tf_reasons.append(f"{tf} Overbought (BB)")
            elif bb_pos < 0.2:
                tf_score += 0.5
                tf_reasons.append(f"{tf} Oversold (BB)")

            # ADX Analysis (Trend Strength)
            adx = data['ADX']
            if adx > 25:
                trend_strength += 1
                if data['ADX+'] > data['ADX-']:
                    tf_score += 1
                    tf_reasons.append(f"{tf} Strong uptrend (ADX: {adx:.2f})")
                else:
                    tf_score -= 1
                    tf_reasons.append(f"{tf} Strong downtrend (ADX: {adx:.2f})")

            # Stochastic Analysis
            if data['Stoch.K'] > data['Stoch.D'] and data['Stoch.K'] < 80:
                tf_score += 0.5
                tf_reasons.append(f"{tf} Stochastic bullish crossover")
            elif data['Stoch.K'] < data['Stoch.D'] and data['Stoch.K'] > 20:
                tf_score -= 0.5
                tf_reasons.append(f"{tf} Stochastic bearish crossover")

            # TradingView Recommendations
            rec_score = {
                'STRONG_BUY': 2, 'BUY': 1, 
                'NEUTRAL': 0, 
                'SELL': -1, 'STRONG_SELL': -2
            }
            tv_rec = data['recommendation']
            tv_score = rec_score.get(tv_rec, 0)
            tf_score += tv_score
            tf_reasons.append(f"{tf} TradingView: {tv_rec}")

            # Add weighted score and reasons for this timeframe
            score += tf_score * weights[tf]
            reasons.extend(tf_reasons)

        return {
            'bias': "bullish" if score > 0 else "bearish",
            'strength': min(5, abs(score) + trend_strength),  # Cap at 5 stars
            'reasons': reasons,
            'trend_strength': trend_strength
        }

    def calculate_position_size(self, entry, stop_loss):
        """Calculate position size based on risk management rules"""
        risk_amount = 100000 * self.risk_per_trade  # Example account size of 100,000
        points_at_risk = abs(entry - stop_loss)
        position_size = int(risk_amount / points_at_risk)
        return position_size

    def generate_trade_plan(self):
        print("\n=== Starting Trade Plan Generation ===\n")
        
        # Get TradingView analysis
        print("1. Getting TradingView analysis...")
        tv_data = self.tv_session.get_analysis()
        if not tv_data or '5m' not in tv_data:
            print("Could not fetch TradingView data")
            return
        
        # Analyze indicators
        print("2. Analyzing indicators across timeframes...")
        analysis = self.analyze_indicators(tv_data)
        if not analysis:
            print("Could not generate analysis")
            return
            
        bias = analysis['bias']
        current_price = tv_data['5m']['close']
        
        # Print analysis
        print("\n=== NIFTY INTRADAY TRADE PLAN ===")
        print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        data_5m = tv_data['5m']
        data_1h = tv_data.get('1h', {})
        
        print(f"\nCurrent Market Status:")
        print(f"Current Price: {current_price:.2f}")
        print(f"Day's High: {data_5m['high']:.2f}")
        print(f"Day's Low: {data_5m['low']:.2f}")
        print(f"Volume: {data_5m['volume']:.0f}")
        
        print(f"\nTechnical Analysis (5 Min):")
        print(f"RSI: {data_5m['RSI']:.2f}")
        print(f"ADX: {data_5m['ADX']:.2f} (Trend Strength)")
        print(f"Stochastic: K={data_5m['Stoch.K']:.2f} D={data_5m['Stoch.D']:.2f}")
        print(f"\nMoving Averages:")
        print(f"EMA20: {data_5m['EMA20']:.2f}")
        print(f"EMA50: {data_5m['EMA50']:.2f}")
        print(f"EMA200: {data_5m['EMA200']:.2f}")
        print(f"\nBollinger Bands:")
        print(f"Upper: {data_5m['BB.upper']:.2f}")
        print(f"Middle: {data_5m['BB.middle']:.2f}")
        print(f"Lower: {data_5m['BB.lower']:.2f}")
        print(f"\nMACD:")
        print(f"MACD Line: {data_5m['MACD.macd']:.2f}")
        print(f"Signal Line: {data_5m['MACD.signal']:.2f}")
        
        print(f"\nTradingView Recommendations:")
        print(f"5min: {data_5m['recommendation']}")
        if '15m' in tv_data:
            print(f"15min: {tv_data['15m']['recommendation']}")
        if '1h' in tv_data:
            print(f"1hour: {tv_data['1h']['recommendation']}")
        
        print(f"\nTrade Setup ({bias.upper()}):")
        print("Trend Strength:", "★" * int(analysis['trend_strength']))
        print("Signal Strength:", "★" * int(analysis['strength']))
        print("\nReasons:")
        for reason in analysis['reasons']:
            print(f"- {reason}")
        
        if bias == "bullish":
            print("\nPRIMARY SETUP (LONG):")
            entry = max(current_price, data_5m['EMA20'])
            stop_loss = min(data_5m['low'], data_5m['BB.lower'])
            target = current_price + (current_price - stop_loss) * self.min_rr_ratio
            
            print(f"Entry: Above {entry:.2f}")
            print(f"Stop Loss: Below {stop_loss:.2f}")
            print(f"Target 1: {target:.2f}")
            pos_size = self.calculate_position_size(entry, stop_loss)
            print(f"Position Size: {pos_size} units")
            
            # Send WhatsApp alert
            alert_message = self.format_trade_alert("bullish", current_price, entry, stop_loss, target, analysis, data_5m)
            self.send_whatsapp_message(alert_message)
            
        else:
            print("\nPRIMARY SETUP (SHORT):")
            entry = min(current_price, data_5m['EMA20'])
            stop_loss = max(data_5m['high'], data_5m['BB.upper'])
            target = current_price - (stop_loss - current_price) * self.min_rr_ratio
            
            print(f"Entry: Below {entry:.2f}")
            print(f"Stop Loss: Above {stop_loss:.2f}")
            print(f"Target 1: {target:.2f}")
            pos_size = self.calculate_position_size(entry, stop_loss)
            print(f"Position Size: {pos_size} units")
            
            # Send WhatsApp alert
            alert_message = self.format_trade_alert("bearish", current_price, entry, stop_loss, target, analysis, data_5m)
            self.send_whatsapp_message(alert_message)
            
        print("\nConfirmation Checklist:")
        print("1. Price vs VWAP & EMA alignment")
        print("2. RSI confirmation (>60 for longs, <40 for shorts)")
        print("3. MACD crossover confirmation")
        print("4. Volume confirmation")
        print("5. Bollinger Bands position")
        print("6. Risk-reward ratio > 1.5:1")
        print("7. Time of day appropriate for trade (avoid 12:30-1:30 PM)")
        
        if tv_data:
            print("\nTradingView Screener Conditions:")
            print("- Minimum 3 technical indicators aligned")
            print("- Price respecting key moving averages")
            print("- Volume above 20-period average")

if __name__ == "__main__":
    try:
        system = TradingSystem()
        system.generate_trade_plan()
    except Exception as e:
        print(f"Error: {str(e)}")
