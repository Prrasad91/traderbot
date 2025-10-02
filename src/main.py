import os
import sys
from datetime import datetime
import pandas as pd

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_collectors.market_data import MarketDataCollector
from src.analysis.technical import TechnicalAnalyzer
from src.analysis.trade_plan import TradePlanGenerator

def main():
    try:
        print("\n=== Starting Trade Plan Generation ===\n")
        
        # Initialize components
        print("1. Initializing components...")
        data_collector = MarketDataCollector()
        technical_analyzer = TechnicalAnalyzer()
        trade_planner = TradePlanGenerator()
        
        print("\n2. Fetching market data...")
        # Collect all required data
        market_data = data_collector.get_nifty_data()
        institutional_data = data_collector.get_institutional_data()
        option_data = data_collector.get_option_chain()
        global_data = data_collector.get_global_indices()
        
        if market_data is None:
            raise Exception("Could not fetch market data")
        
        print("\n3. Analyzing technical indicators...")
        # Perform technical analysis
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
        # Generate trade plan
        trade_plan = trade_planner.generate_trade_plan(
            market_data,
            technical_data,
            institutional_data,
            option_data,
            global_data
        )
        
        # Print trade plan in a formatted way
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
