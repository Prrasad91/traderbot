from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
from datetime import datetime
import requests

def get_nifty_option_chain():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error fetching option chain: {str(e)}")
        return None

def suggest_option_trade(current_price, bias, strength):
    # Round to nearest 50 for strike selection
    atm_strike = round(current_price / 50) * 50
    
    if bias == "BUY":
        trade_type = "CALL"
        entry_strike = atm_strike
        hedge_strike = atm_strike + 200
    elif bias == "SELL":
        trade_type = "PUT"
        entry_strike = atm_strike
        hedge_strike = atm_strike - 200
    else:
        return None
    
    # Strategy based on strength
    if strength >= 3:  # Strong trend
        strategy = "Simple Options Buy"
        suggestion = f"{trade_type} option at strike {entry_strike}"
    else:  # Moderate trend
        strategy = "Bull/Bear Spread"
        if trade_type == "CALL":
            suggestion = f"Buy {entry_strike} CALL & Sell {hedge_strike} CALL"
        else:
            suggestion = f"Buy {entry_strike} PUT & Sell {hedge_strike} PUT"
    
    return {
        'strategy': strategy,
        'suggestion': suggestion,
        'primary_strike': entry_strike,
        'hedge_strike': hedge_strike,
        'trade_type': trade_type
    }

def calculate_signal_strength(analysis):
    strength = 0
    
    # RSI Analysis
    rsi = analysis.indicators['RSI']
    if (rsi > 60 and analysis.summary['RECOMMENDATION'] in ['BUY', 'STRONG_BUY']) or \
       (rsi < 40 and analysis.summary['RECOMMENDATION'] in ['SELL', 'STRONG_SELL']):
        strength += 1
    
    # MACD Analysis
    macd = analysis.indicators['MACD.macd']
    signal = analysis.indicators['MACD.signal']
    if (macd > signal and analysis.summary['RECOMMENDATION'] in ['BUY', 'STRONG_BUY']) or \
       (macd < signal and analysis.summary['RECOMMENDATION'] in ['SELL', 'STRONG_SELL']):
        strength += 1
    
    # Moving Averages
    if analysis.moving_averages['RECOMMENDATION'] == analysis.summary['RECOMMENDATION']:
        strength += 1
    
    # Oscillators
    if analysis.oscillators['RECOMMENDATION'] == analysis.summary['RECOMMENDATION']:
        strength += 1
    
    return strength

def main():
    try:
        print("\n=== Starting Trade Plan Generation ===\n")
        
        # Initialize TradingView handler
        handler = TA_Handler(
            symbol="NIFTY",
            exchange="NSE",
            screener="india",
            interval=Interval.INTERVAL_5_MINUTES
        )
        
        print("\nFetching market data...")
        analysis = handler.get_analysis()
        
        # Create market data DataFrame
        market_data = pd.DataFrame({
            'Timestamp': [datetime.now()],
            'Close': [analysis.indicators['close']],
            'RSI': [analysis.indicators['RSI']],
            'MACD': [analysis.indicators['MACD.macd']],
            'Signal': [analysis.indicators['MACD.signal']]
        })
        
        # Print analysis
        print("\n=== NIFTY ANALYSIS ===")
        print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\nPRICE ACTION:")
        print(f"Current Price: ₹{analysis.indicators['close']:.2f}")
        print(f"Day High: ₹{analysis.indicators['high']:.2f}")
        print(f"Day Low: ₹{analysis.indicators['low']:.2f}")
        
        print("\nTECHNICAL INDICATORS:")
        print(f"RSI: {analysis.indicators['RSI']:.2f}")
        print(f"MACD Line: {analysis.indicators['MACD.macd']:.2f}")
        print(f"Signal Line: {analysis.indicators['MACD.signal']:.2f}")
        
        print("\nTRADING SIGNALS:")
        print(f"Overall: {analysis.summary['RECOMMENDATION']}")
        print(f"Moving Averages: {analysis.moving_averages['RECOMMENDATION']}")
        print(f"Oscillators: {analysis.oscillators['RECOMMENDATION']}")
        
        # Calculate signal strength and generate option trade suggestions
        signal_strength = calculate_signal_strength(analysis)
        current_price = analysis.indicators['close']
        
        print("\nTRADE SETUP:")
        print(f"Signal Strength: {signal_strength}/4 (Higher is stronger)")
        
        if signal_strength >= 2:  # Only suggest trades if signal strength is moderate to strong
            trade_suggestion = suggest_option_trade(
                current_price=current_price,
                bias=analysis.summary['RECOMMENDATION'],
                strength=signal_strength
            )
            
            if trade_suggestion:
                print(f"\nRECOMMENDED STRATEGY: {trade_suggestion['strategy']}")
                print(f"TRADE SUGGESTION: {trade_suggestion['suggestion']}")
                print("\nRISK MANAGEMENT:")
                print(f"Stop Loss: Place stop loss at 30-40% of option premium")
                print(f"Target: Book profits at 60-80% of option premium")
                
                # Option Chain Analysis
                print("\nFetching Option Chain data...")
                option_chain = get_nifty_option_chain()
                if option_chain:
                    print("Option Chain data available - Validate premiums before entry")
                else:
                    print("Unable to fetch live option chain - Check NSE website for current premiums")
            else:
                print("\nNo clear option trade setup at current levels")
        else:
            print("\nWEAK SIGNALS - Better to avoid trading at current levels")
            print("Wait for stronger directional bias to emerge")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        return

if __name__ == "__main__":
    main()
