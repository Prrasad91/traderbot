import pandas as pd
import numpy as np
from datetime import datetime, date

class TechnicalAnalyzer:
    def calculate_vwap(self, data):
        df = data.copy()
        df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
        df['VP'] = df['Typical_Price'] * df['Volume']
        df['Cumulative_VP'] = df['VP'].cumsum()
        df['Cumulative_Volume'] = df['Volume'].cumsum()
        df['VWAP'] = df['Cumulative_VP'] / df['Cumulative_Volume']
        return df

    def identify_trend(self, data, period=20):
        if len(data) < period:
            return "undefined"
        return "uptrend" if data['Close'].iloc[-1] > data['Close'].mean() else "downtrend"

    def identify_key_levels(self, data):
        return {
            'high': float(data['High'].max()),
            'low': float(data['Low'].min()),
            'prev_close': float(data['Prev Close'].iloc[-1]),
            'vwap': float(data['VWAP'].iloc[-1]) if 'VWAP' in data.columns else None
        }

    def validate_momentum(self, data, period=14):
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0).mean()
        loss = -delta.where(delta < 0, 0).mean()
        rs = gain / loss if loss != 0 else 0
        rsi = 100 - (100 / (1 + rs))
        return {'momentum': 'bullish' if rsi > 50 else 'bearish', 'rsi': rsi}

    def identify_candlestick_pattern(self, data):
        row = data.iloc[-1]
        body = abs(row['Close'] - row['Open'])
        if body < (row['High'] - row['Low']) * 0.2:
            return "doji"
        return "no_pattern"

class MarketDataCollector:
    def get_nifty_data(self):
        df = pd.DataFrame({
            'Open': [19500],
            'High': [19600],
            'Low': [19400],
            'Close': [19550],
            'Volume': [1000000],
            'Prev Close': [19480]
        }, index=[pd.Timestamp.now()])
        return df

    def get_institutional_data(self):
        return {
            "FII": {
                "cash_flow": 1250.5,
                "futures_oi": 850.75,
                "options_oi": 1500.25
            },
            "DII": {
                "cash_flow": 750.25,
                "futures_oi": 0,
                "options_oi": 0
            }
        }

    def get_option_chain(self):
        current_price = 19550
        strikes = range(int(current_price - 500), int(current_price + 500), 100)
        calls = []
        puts = []
        total_call_oi = 0
        total_put_oi = 0
        
        for strike in strikes:
            base_oi = max(10000 - abs(strike - current_price), 1000)
            call_oi = base_oi + np.random.randint(-500, 500)
            put_oi = base_oi + np.random.randint(-500, 500)
            
            calls.append({"strike": strike, "oi": call_oi, "change_oi": np.random.randint(-200, 200)})
            puts.append({"strike": strike, "oi": put_oi, "change_oi": np.random.randint(-200, 200)})
            
            total_call_oi += call_oi
            total_put_oi += put_oi
        
        return {
            "calls": calls,
            "puts": puts,
            "pcr": round(total_put_oi / total_call_oi, 2)
        }

    def get_global_indices(self):
        return {
            'NIFTY 50': {"price": 19550.25, "change": 125.75, "change_percent": 0.65},
            'NIFTY BANK': {"price": 44250.50, "change": 350.25, "change_percent": 0.80},
            'INDIA VIX': {"price": 12.75, "change": -0.50, "change_percent": -3.77},
            'NIFTY NEXT 50': {"price": 45750.25, "change": 225.50, "change_percent": 0.50}
        }

class TradePlanGenerator:
    def __init__(self):
        self.max_trades_per_day = 2
        self.stop_loss_percent = 0.5
        self.square_off_time = "15:15"

    def _analyze_institutional_bias(self, institutional_data):
        if not institutional_data:
            return "neutral"
        fii = institutional_data.get('FII', {})
        dii = institutional_data.get('DII', {})
        fii_net = fii.get('cash_flow', 0) + fii.get('futures_oi', 0)
        dii_net = dii.get('cash_flow', 0)
        
        if fii_net > 0 and dii_net > 0:
            return "strongly_bullish"
        elif fii_net > 0:
            return "moderately_bullish"
        elif fii_net < 0 and dii_net < 0:
            return "strongly_bearish"
        elif fii_net < 0:
            return "moderately_bearish"
        return "neutral"

    def _analyze_option_chain(self, option_data):
        if not option_data:
            return "neutral"
        pcr = option_data.get('pcr', 0)
        if pcr > 1.5:
            return "bullish"
        elif pcr < 0.7:
            return "bearish"
        return "neutral"

    def _analyze_global_cues(self, global_data):
        if not global_data:
            return "neutral"
        positive_count = sum(1 for index in global_data.values() if index.get('change_percent', 0) > 0)
        negative_count = sum(1 for index in global_data.values() if index.get('change_percent', 0) <= 0)
        if positive_count > negative_count:
            return "bullish"
        elif negative_count > positive_count:
            return "bearish"
        return "neutral"

    def _determine_overall_bias(self, inst_bias, option_bias, global_bias):
        bias_map = {
            "strongly_bullish": 2, "moderately_bullish": 1, "bullish": 1,
            "neutral": 0,
            "moderately_bearish": -1, "bearish": -1, "strongly_bearish": -2
        }
        total_score = (bias_map.get(inst_bias, 0) * 2 +
                      bias_map.get(option_bias, 0) +
                      bias_map.get(global_bias, 0))
        if total_score >= 2:
            return "bullish"
        elif total_score <= -2:
            return "bearish"
        return "neutral"

    def generate_trade_plan(self, market_data, technical_data, institutional_data, option_data, global_data):
        inst_bias = self._analyze_institutional_bias(institutional_data)
        option_bias = self._analyze_option_chain(option_data)
        global_bias = self._analyze_global_cues(global_data)
        overall_bias = self._determine_overall_bias(inst_bias, option_bias, global_bias)

        key_levels = technical_data.get('key_levels', {})
        primary_setup = None
        alternate_setup = None

        if overall_bias == "bullish":
            primary_setup = {
                "type": "long",
                "entry": f"Above {key_levels.get('prev_close')} with volume confirmation",
                "stop_loss": key_levels.get('low'),
                "target": key_levels.get('high'),
                "confirmation": "Price above VWAP"
            }
            alternate_setup = {
                "type": "short",
                "entry": f"Below {key_levels.get('low')} with heavy selling pressure",
                "stop_loss": key_levels.get('vwap'),
                "target": f"{key_levels.get('low')} - 0.5%",
                "confirmation": "Break of support with volume"
            }
        elif overall_bias == "bearish":
            primary_setup = {
                "type": "short",
                "entry": f"Below {key_levels.get('prev_close')} with volume confirmation",
                "stop_loss": key_levels.get('high'),
                "target": key_levels.get('low'),
                "confirmation": "Price below VWAP"
            }
            alternate_setup = {
                "type": "long",
                "entry": f"Above {key_levels.get('high')} with heavy buying pressure",
                "stop_loss": key_levels.get('vwap'),
                "target": f"{key_levels.get('high')} + 0.5%",
                "confirmation": "Break of resistance with volume"
            }

        return {
            "market_bias": {
                "institutional": inst_bias,
                "options": option_bias,
                "global": global_bias,
                "overall": overall_bias
            },
            "setups": {
                "primary": primary_setup,
                "alternate": alternate_setup
            },
            "risk_management": {
                "max_trades": self.max_trades_per_day,
                "stop_loss_percent": self.stop_loss_percent,
                "square_off_time": self.square_off_time
            },
            "confirmation_checklist": [
                "VWAP alignment with trade direction",
                "Volume confirmation",
                "Candlestick pattern confirmation",
                "No contradicting institutional flow",
                "Risk-reward ratio > 1:1",
                "Not too close to day's high/low",
                "Market breadth supporting the move",
                "Time of day appropriate for trade"
            ]
        }

def main():
    try:
        print("\n=== Starting Trade Plan Generation ===\n")
        
        # Initialize components
        print("1. Initializing components...")
        data_collector = MarketDataCollector()
        technical_analyzer = TechnicalAnalyzer()
        trade_planner = TradePlanGenerator()
        
        print("\n2. Fetching market data...")
        market_data = data_collector.get_nifty_data()
        institutional_data = data_collector.get_institutional_data()
        option_data = data_collector.get_option_chain()
        global_data = data_collector.get_global_indices()
        
        if market_data is None:
            raise Exception("Could not fetch market data")
        
        print("\n3. Analyzing technical indicators...")
        market_data = technical_analyzer.calculate_vwap(market_data)
        trend = technical_analyzer.identify_trend(market_data)
        key_levels = technical_analyzer.identify_key_levels(market_data)
        momentum = technical_analyzer.validate_momentum(market_data)
        pattern = technical_analyzer.identify_candlestick_pattern(market_data)
        
        technical_data = {
            'trend': trend,
            'key_levels': key_levels,
            'momentum': momentum,
            'pattern': pattern,
            'vwap': market_data['VWAP'].iloc[-1] if 'VWAP' in market_data.columns else None
        }
        
        print("\n4. Generating trade plan...")
        trade_plan = trade_planner.generate_trade_plan(
            market_data,
            technical_data,
            institutional_data,
            option_data,
            global_data
        )
        
        print("\n=== NIFTY INTRADAY TRADE PLAN ===")
        print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\nMARKET BIAS:")
        for bias_type, bias in trade_plan['market_bias'].items():
            print(f"- {bias_type.capitalize()}: {bias}")
        
        print("\nPRIMARY SETUP:")
        if trade_plan['setups']['primary']:
            setup = trade_plan['setups']['primary']
            print(f"Type: {setup['type'].upper()}")
            print(f"Entry: {setup['entry']}")
            print(f"Stop Loss: {setup['stop_loss']}")
            print(f"Target: {setup['target']}")
            print(f"Confirmation: {setup['confirmation']}")
        else:
            print("No clear primary setup")
        
        print("\nALTERNATE SETUP:")
        if trade_plan['setups']['alternate']:
            setup = trade_plan['setups']['alternate']
            print(f"Type: {setup['type'].upper()}")
            print(f"Entry: {setup['entry']}")
            print(f"Stop Loss: {setup['stop_loss']}")
            print(f"Target: {setup['target']}")
            print(f"Confirmation: {setup['confirmation']}")
        else:
            print("No clear alternate setup")
        
        print("\nRISK MANAGEMENT:")
        risk = trade_plan['risk_management']
        print(f"- Max trades per day: {risk['max_trades']}")
        print(f"- Stop loss per trade: {risk['stop_loss_percent']}%")
        print(f"- Square off time: {risk['square_off_time']}")
        
        print("\nCONFIRMATION CHECKLIST:")
        for i, item in enumerate(trade_plan['confirmation_checklist'], 1):
            print(f"{i}. {item}")
            
    except Exception as e:
        print(f"\nError in trade plan generation: {str(e)}")
        return

if __name__ == "__main__":
    main()
