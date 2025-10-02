"""Trading system using TradingView data for Nifty analysis"""
import pandas as pd
import numpy as np
from datetime import datetime
from time import sleep
from tradingview_ta import TA_Handler, Interval, Exchange

class TradingViewSession:
    def __init__(self):
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

    def get_analysis(self):
        """Get technical analysis data from TradingView"""
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
            print(f"Error in get_analysis: {str(e)}")
            return None

class TradingSystem:
    def __init__(self):
        self.tv_session = TradingViewSession()
        self.last_data = None
        self.risk_per_trade = 0.01  # 1% risk per trade
        self.min_rr_ratio = 1.5  # Minimum risk-reward ratio

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
            pos_size = self.calculate_position_size(entry, stop_loss)
            print(f"Entry: Above {entry:.2f}")
            print(f"Stop Loss: Below {stop_loss:.2f}")
            print(f"Target 1: {target:.2f}")
            print(f"Position Size: {pos_size} units")
        else:
            print("\nPRIMARY SETUP (SHORT):")
            entry = min(current_price, data_5m['EMA20'])
            stop_loss = max(data_5m['high'], data_5m['BB.upper'])
            target = current_price - (stop_loss - current_price) * self.min_rr_ratio
            pos_size = self.calculate_position_size(entry, stop_loss)
            print(f"Entry: Below {entry:.2f}")
            print(f"Stop Loss: Above {stop_loss:.2f}")
            print(f"Target 1: {target:.2f}")
            print(f"Position Size: {pos_size} units")
        
        risk = abs(entry - stop_loss)
        reward = abs(target - entry)
        rr_ratio = reward / risk if risk > 0 else 0
        
        print(f"\nRisk Analytics:")
        print(f"Points at Risk: {risk:.2f}")
        print(f"Potential Reward: {reward:.2f}")
        print(f"Risk:Reward Ratio: {rr_ratio:.2f}")
        
        print("\nEntry Rules:")
        print("1. Trend alignment across timeframes")
        print("2. RSI momentum confirmation")
        print("3. MACD crossover signal")
        print("4. Volume surge confirmation")
        print("5. Key level breakout")
        
        print("\nExit Rules:")
        print("1. Target achieved")
        print("2. Stop loss hit")
        print("3. Trend reversal signals:")
        print("   - MACD crossover against position")
        print("   - RSI divergence")
        print("   - Break of key moving average")
        
        current_hour = datetime.now().hour
        current_minute = datetime.now().minute
        if 9 <= current_hour < 15 or (current_hour == 15 and current_minute <= 15):
            if 12 <= current_hour < 13:
                print("\nCAUTION: Lunch hour (12:00-1:00 PM), expect low volume and choppy moves")
            elif current_hour < 10:
                print("\nCAUTION: Opening hour, wait for market direction to establish")
            elif current_hour >= 15:
                print("\nCAUTION: Near market close, consider booking profits")
        else:
            print("\nMarket is closed. Use this analysis for next day's planning.")

if __name__ == "__main__":
    try:
        system = TradingSystem()
        system.generate_trade_plan()
    except Exception as e:
        print(f"Error: {str(e)}")
