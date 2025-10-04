from tradingview_ta import TA_Handler, Interval
import pandas as pd
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.analysis.technical import TechnicalAnalyzer

def main():
    try:
        print("\n=== Starting Trading Analysis ===\n")
        
        # Initialize TradingView handler for NIFTY
        handler = TA_Handler(
            symbol="NIFTY",
            exchange="NSE",
            screener="india",
            interval=Interval.INTERVAL_5_MINUTES
        )
        
        print("Fetching market data...")
        analysis = handler.get_analysis()
        
        # Create market data DataFrame
        market_data = pd.DataFrame({
            'Open': [analysis.indicators['open']],
            'High': [analysis.indicators['high']],
            'Low': [analysis.indicators['low']],
            'Close': [analysis.indicators['close']],
            'Volume': [analysis.indicators['volume']],
            'RSI': [analysis.indicators['RSI']],
            'MACD': [analysis.indicators['MACD.macd']],
            'MACD_Signal': [analysis.indicators['MACD.signal']],
            'ADX': [analysis.indicators['ADX']]
        })
        
        # Initialize Technical Analyzer
        analyzer = TechnicalAnalyzer()
        
        # Add VWAP
        market_data = analyzer.calculate_vwap(market_data)
        
        print("\nAnalyzing market conditions...")
        # Check for signals and send alerts
        analysis_result = analyzer.check_and_send_alerts(market_data)
        
        # Print basic analysis
        if analysis_result:
            trend_info = analysis_result['trend']
            momentum_info = analysis_result['momentum']
            print(f"\nCurrent Analysis:")
            print(f"Trend: {trend_info['trend'].upper()} (Strength: {trend_info['strength']}/5)")
            print(f"Momentum: {momentum_info['momentum'].upper()} (Strength: {momentum_info['strength']}/5)")
            print(f"Current Price: ₹{market_data['Close'].iloc[-1]:.2f}")
        
        print("\nAnalysis complete. Check email for major signals.")
        
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()
