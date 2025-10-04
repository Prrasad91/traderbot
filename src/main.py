import os
import sys
import time
from datetime import datetime
import pandas as pd
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from data_collectors.market_data import MarketDataCollector
from analysis.technical import TechnicalAnalyzer
from analysis.trade_plan import TradePlanGenerator
import config import datetime
import pandas as pd
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from .data_collectors.market_data import MarketDataCollector
from .analysis.technical import TechnicalAnalyzer
from .analysis.trade_plan import TradePlanGenerator
from datetime import datetime
import pandas as pd

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .data_collectors.market_data import MarketDataCollector
from .analysis.technical import TechnicalAnalyzer
from .analysis.trade_plan import TradePlanGenerator

def is_market_open():
    now = datetime.now().time()
    start = datetime.strptime(config.MARKET_START, "%H:%M").time()
    end = datetime.strptime(config.MARKET_END, "%H:%M").time()
    return start <= now <= end

def main():
    try:
        print("\n=== Starting Trading System ===\n")
        
        # Initialize components
        print("Initializing components...")
        data_collector = MarketDataCollector()
        technical_analyzer = TechnicalAnalyzer()
        trade_planner = TradePlanGenerator()
        last_alert_time = None
        
        while True:
            try:
                if not is_market_open():
                    print("\nMarket is closed. Waiting for market hours...")
                    time.sleep(300)  # Check every 5 minutes
                    continue
                
                print("\nFetching market data...")
                # Collect all required data
                market_data = data_collector.get_nifty_data()
                institutional_data = data_collector.get_institutional_data()
                option_data = data_collector.get_option_chain()
                global_data = data_collector.get_global_indices()
                
                if market_data is None:
                    raise Exception("Could not fetch market data")
                    
                # Process each timeframe
                technical_data = {}
                for interval in market_data:
                    data = market_data[interval]['data']
                    data = technical_analyzer.calculate_vwap(data)
                    
                    technical_data[interval] = {
                        'trend': technical_analyzer.identify_trend(data),
                        'key_levels': technical_analyzer.identify_key_levels(data),
                        'momentum': technical_analyzer.validate_momentum(data),
                        'pattern': technical_analyzer.identify_candlestick_pattern(data),
                        'vwap': data['VWAP'].iloc[-1] if 'VWAP' in data.columns else None,
                        'summary': market_data[interval]['summary'],
                        'moving_averages': market_data[interval]['moving_averages'],
                        'oscillators': market_data[interval]['oscillators']
                    }
                
                # Generate trade plan
                trade_plan = trade_planner.generate_trade_plan(
                    market_data["5m"]['data'],  # Use 5m for current price
                    technical_data,
                    institutional_data,
                    option_data,
                    global_data
                )
                
                # Print analysis
                print(f"\n=== NIFTY ANALYSIS === ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
                
                current_price = market_data["5m"]['data']['Close'].iloc[-1]
                print(f"\nPrice: ₹{current_price:.2f}")
                print(f"VWAP: ₹{technical_data['5m']['vwap']:.2f}")
                
                print("\nMarket Bias:")
                for bias_type, bias in trade_plan['market_bias'].items():
                    print(f"- {bias_type.capitalize()}: {bias}")
                
                if trade_plan['setups']['primary']:
                    setup = trade_plan['setups']['primary']
                    print(f"\nPrimary Setup ({setup['type'].upper()}):")
                    print(f"Entry: ₹{setup['entry']:.2f}")
                    print(f"Stop Loss: ₹{setup['stop_loss']:.2f}")
                    print(f"Target: ₹{setup['target']:.2f}")
                
                print("\nSignal Strengths:")
                for interval in technical_data:
                    trend = technical_data[interval]['trend']
                    momentum = technical_data[interval]['momentum']
                    print(f"{interval}: Trend={trend['strength']}/5, Momentum={momentum['strength']}/5")
                
                # Wait before next analysis
                print("\nWaiting 30 seconds for next analysis...")
                time.sleep(30)
                
            except Exception as loop_error:
                print(f"\nError in analysis loop: {str(loop_error)}")
                print("Retrying in 30 seconds...")
                time.sleep(30)
                
    except KeyboardInterrupt:
        print("\n\nTrading system stopped by user")
    except Exception as e:
        print(f"\nCritical error: {str(e)}")
        return
        
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
