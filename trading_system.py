from tradingview_ta import TA_Handler, Interval
import pandas as pd
from datetime import datetime
import time

def main():
    try:
        print("\n=== Starting Trading System ===\n")
        
        # Initialize TradingView handler
        handlers = {
            "5m": TA_Handler(
                symbol="NIFTY",
                exchange="NSE",
                screener="india",
                interval=Interval.INTERVAL_5_MINUTES
            ),
            "15m": TA_Handler(
                symbol="NIFTY",
                exchange="NSE",
                screener="india",
                interval=Interval.INTERVAL_15_MINUTES
            ),
            "1h": TA_Handler(
                symbol="NIFTY",
                exchange="NSE",
                screener="india",
                interval=Interval.INTERVAL_1_HOUR
            )
        }
        
        while True:
            try:
                print("\nFetching market data...")
                all_data = {}
                
                # Get analysis for each timeframe
                for interval, handler in handlers.items():
                    analysis = handler.get_analysis()
                    indicators = analysis.indicators
                    
                    print(f"\n=== {interval} Timeframe Analysis ===")
                    print(f"Price: ₹{indicators['close']:.2f}")
                    print(f"RSI: {indicators['RSI']:.2f}")
                    print(f"MACD: {indicators['MACD.macd']:.2f}")
                    print(f"Signal: {indicators['MACD.signal']:.2f}")
                    print(f"ADX: {indicators['ADX']:.2f}")
                    print(f"Recommendation: {analysis.summary['RECOMMENDATION']}")
                    
                    # Store data for trend analysis
                    all_data[interval] = {
                        'price': indicators['close'],
                        'rsi': indicators['RSI'],
                        'adx': indicators['ADX'],
                        'macd': indicators['MACD.macd'],
                        'signal': indicators['MACD.signal'],
                        'recommendation': analysis.summary['RECOMMENDATION']
                    }
                
                # Overall analysis
                print("\n=== Overall Market Analysis ===")
                
                # Trend strength
                adx_5m = all_data['5m']['adx']
                if adx_5m > 25:
                    trend_strength = "Strong"
                elif adx_5m > 20:
                    trend_strength = "Moderate"
                else:
                    trend_strength = "Weak"
                
                # Bias calculation
                bullish_signals = 0
                bearish_signals = 0
                
                for interval, data in all_data.items():
                    if data['rsi'] > 60:
                        bullish_signals += 1
                    elif data['rsi'] < 40:
                        bearish_signals += 1
                        
                    if data['macd'] > data['signal']:
                        bullish_signals += 1
                    else:
                        bearish_signals += 1
                        
                    if data['recommendation'] in ['STRONG_BUY', 'BUY']:
                        bullish_signals += 1
                    elif data['recommendation'] in ['STRONG_SELL', 'SELL']:
                        bearish_signals += 1
                
                # Final bias
                if bullish_signals > bearish_signals + 2:
                    bias = "BULLISH"
                elif bearish_signals > bullish_signals + 2:
                    bias = "BEARISH"
                else:
                    bias = "NEUTRAL"
                
                print(f"Current Price: ₹{all_data['5m']['price']:.2f}")
                print(f"Trend Strength: {trend_strength}")
                print(f"Market Bias: {bias}")
                print(f"Bullish Signals: {bullish_signals}")
                print(f"Bearish Signals: {bearish_signals}")
                
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

if __name__ == "__main__":
    main()
