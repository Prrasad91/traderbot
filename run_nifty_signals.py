from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
from datetime import datetime
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email configuration
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'sriram86rs@gmail.com',
    'sender_password': 'rlcd rmyu zshb eajy',
    'recipients': ['venkateshprasad.s@hotmail.com']
}

def send_alert(subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = ', '.join(EMAIL_CONFIG['recipients'])
        msg['Subject'] = f"NIFTY Alert: {subject}"
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
        server.send_message(msg)
        server.quit()
        
        print("Alert email sent successfully!")
        return True
        
    except Exception as e:
        print(f"Failed to send email alert: {str(e)}")
        return False

def generate_trading_signals():
    print("\n=== Starting Nifty Analysis ===")
    
    try:
        # Initialize TradingView handler for NIFTY
        handler = TA_Handler(
            symbol="NIFTY",
            exchange="NSE",
            screener="india",
            interval=Interval.INTERVAL_5_MINUTES
        )
        
        print("\nFetching market data...")
        analysis = handler.get_analysis()
        
        # Get current price and indicators
        current_price = analysis.indicators['close']
        rsi = analysis.indicators['RSI']
        macd = analysis.indicators['MACD.macd']
        macd_signal = analysis.indicators['MACD.signal']
        adx = analysis.indicators['ADX']
        
        # Calculate nearest strike price
        atm_strike = round(current_price / 50) * 50
        
        # Determine trend and strength
        trend = "NEUTRAL"
        strength = 0
        
        # RSI Analysis (0-100)
        if rsi > 60:
            trend = "BULLISH"
            strength += 2
        elif rsi < 40:
            trend = "BEARISH"
            strength += 2
        
        # MACD Analysis
        if macd > macd_signal:
            if trend == "BULLISH":
                strength += 2
            elif trend == "NEUTRAL":
                trend = "BULLISH"
                strength += 1
        elif macd < macd_signal:
            if trend == "BEARISH":
                strength += 2
            elif trend == "NEUTRAL":
                trend = "BEARISH"
                strength += 1
        
        # ADX Strength (0-100)
        if adx > 25:
            strength += 1
        
        # Print analysis
        print(f"\nCurrent Price: ₹{current_price:.2f}")
        print(f"ATM Strike: {atm_strike}")
        print(f"\nINDICATORS:")
        print(f"RSI: {rsi:.2f}")
        print(f"MACD: {macd:.2f}")
        print(f"MACD Signal: {macd_signal:.2f}")
        print(f"ADX: {adx:.2f}")
        print(f"\nANALYSIS:")
        print(f"Trend: {trend}")
        print(f"Signal Strength: {strength}/5")
        
        # Generate trading recommendations if signal is strong enough
        if strength >= 3:
            # Calculate support and resistance levels
            support_1 = round(current_price * 0.995, 2)
            support_2 = round(current_price * 0.99, 2)
            resistance_1 = round(current_price * 1.005, 2)
            resistance_2 = round(current_price * 1.01, 2)
            
            message = [
                f"=== NIFTY TRADING SIGNAL ===",
                f"\nPrice: ₹{current_price:.2f}",
                f"Trend: {trend}",
                f"Signal Strength: {strength}/5",
                f"\nTECHNICAL INDICATORS:",
                f"RSI: {rsi:.2f}",
                f"MACD: {macd:.2f}",
                f"ADX: {adx:.2f}",
                "\nRECOMMENDED TRADES:"
            ]
            
            if trend == "BULLISH":
                message.extend([
                    f"\n1. Options Strategy (Conservative):",
                    f"   - Buy {atm_strike} Call",
                    f"   - Sell {atm_strike + 200} Call (Bear Spread)",
                    f"\n2. Options Strategy (Aggressive):",
                    f"   - Buy {atm_strike} Call",
                    f"   - Target: 50-70% profit",
                    f"   - Stop Loss: 30% of premium",
                    f"\nPrice Targets:",
                    f"Target 1: ₹{resistance_1}",
                    f"Target 2: ₹{resistance_2}",
                    f"Stop Loss: ₹{support_2}"
                ])
            else:  # BEARISH
                message.extend([
                    f"\n1. Options Strategy (Conservative):",
                    f"   - Buy {atm_strike} Put",
                    f"   - Sell {atm_strike - 200} Put (Bull Spread)",
                    f"\n2. Options Strategy (Aggressive):",
                    f"   - Buy {atm_strike} Put",
                    f"   - Target: 50-70% profit",
                    f"   - Stop Loss: 30% of premium",
                    f"\nPrice Targets:",
                    f"Target 1: ₹{support_1}",
                    f"Target 2: ₹{support_2}",
                    f"Stop Loss: ₹{resistance_2}"
                ])
            
            message.extend([
                "\nRISK MANAGEMENT:",
                "1. Use strict stop loss",
                "2. Max risk: 2% of capital per trade",
                "3. Exit half position at Target 1",
                "4. Trail stop loss after Target 1",
                "5. Book profits at end of day if targets not hit"
            ])
            
            # Send alert
            signal_type = "BUY" if trend == "BULLISH" else "SELL"
            send_alert(f"{signal_type} Signal", "\n".join(message))
            print("\nTrading signal generated and alert sent!")
        else:
            print("\nNo strong trading signals at current levels")
        
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")

def main():
    while True:
        try:
            generate_trading_signals()
            print("\nWaiting 5 minutes before next analysis...")
            time.sleep(300)  # Wait 5 minutes
        except KeyboardInterrupt:
            print("\nAnalysis stopped by user")
            break
        except Exception as e:
            print(f"\nError in main loop: {str(e)}")
            print("Retrying in 30 seconds...")
            time.sleep(30)

if __name__ == "__main__":
    main()
