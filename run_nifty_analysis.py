from src.analysis.technical import TechnicalAnalyzer
import pandas_ta as ta
import time
import pandas as pd

def prepare_data(df):
    """Add technical indicators to the dataframe"""
    if df is None or len(df) == 0:
        return None
        
    # Calculate RSI
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    # Calculate MACD
    macd = ta.macd(df['Close'])
    df['MACD'] = macd['MACD_12_26_9']
    df['MACD_Signal'] = macd['MACDs_12_26_9']
    
    # Calculate ADX
    adx = ta.adx(df['High'], df['Low'], df['Close'])
    df['ADX'] = adx['ADX_14']
    
    return df

def main():
    analyzer = TechnicalAnalyzer()
    
    print("Starting NIFTY Analysis...")
    
    try:
        # Fetch market data
        df = analyzer.fetch_nifty_data(interval='5m', period='1d')
        if df is None:
            print("Failed to fetch NIFTY data")
            return
            
        # Add technical indicators
        df = prepare_data(df)
        if df is None:
            print("Failed to prepare data")
            return
            
        # Calculate VWAP
        df = analyzer.calculate_vwap(df)
        
        # Check for signals and send alerts
        analysis = analyzer.check_and_send_alerts(df)
        
        if analysis:
            print("\nAnalysis Results:")
            print(f"Trend: {analysis['trend']['trend']} (Strength: {analysis['trend']['strength']}/5)")
            print(f"Momentum: {analysis['momentum']['momentum']} (Strength: {analysis['momentum']['strength']}/5)")
            
            if analysis['patterns']:
                print(f"Patterns: {', '.join(analysis['patterns'])}")
                
            if 'market_sentiment' in analysis and analysis['market_sentiment']:
                sentiment = analysis['market_sentiment']
                print(f"\nMarket Sentiment:")
                print(f"Price Trend: {sentiment['price_trend']}")
                print(f"Volume Trend: {sentiment['volume_trend']}")
                print(f"Volatility: {sentiment['volatility']:.2f}%")
                if 'vix' in sentiment:
                    print(f"VIX: {sentiment['vix']:.2f} (Change: {sentiment['vix_change']:.2f})")
                    
            if 'market_status' in analysis and analysis['market_status']:
                print(f"\nMarket Status: {analysis['market_status']['market_status']}")
                print(f"Last Update: {analysis['market_status']['last_update']}")
                
        print("\nAnalysis completed.")
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    main()
