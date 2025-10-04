"""
Main entry point for the trading bot
"""
from tradingview_ta import TA_Handler, Interval
import pandas as pd
from datetime import datetime

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
        print(f"ADX: {analysis.indicators['ADX']:.2f}")
        
        # Trend strength based on ADX
        if analysis.indicators['ADX'] > 25:
            trend_strength = "Strong"
        elif analysis.indicators['ADX'] > 20:
            trend_strength = "Moderate"
        else:
            trend_strength = "Weak"
            
        print(f"Trend Strength: {trend_strength}")
        print("\nTRADING SIGNALS:")
        print(f"Overall: {analysis.summary['RECOMMENDATION']}")
        print(f"Moving Averages: {analysis.moving_averages['RECOMMENDATION']}")
        print(f"Oscillators: {analysis.oscillators['RECOMMENDATION']}")
        
        # Calculate trend strength
        if analysis.indicators['ADX'] > 25:
            trend_strength = "Strong"
        elif analysis.indicators['ADX'] > 20:
            trend_strength = "Moderate"
        else:
            trend_strength = "Weak"
        
        print(f"\nTrend Strength: {trend_strength} (ADX: {analysis.indicators['ADX']:.2f})")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        return

if __name__ == "__main__":
    main()
