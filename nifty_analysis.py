from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from scipy.stats import norm
from sklearn.cluster import KMeans

# Email configuration
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'sriram86rs@gmail.com',
    'sender_password': 'rlcd rmyu zshb eajy',
    'recipients': ['venkateshprasad.s@hotmail.com']
}

class NiftyAnalyzer:
    def __init__(self):
        self.vwap_period = 20
        self.last_alert_time = None
        self.alert_cooldown_minutes = 30
        
    def send_email_alert(self, subject, body):
        try:
            current_time = datetime.now()
            
            if self.last_alert_time and (current_time - self.last_alert_time).total_seconds() < self.alert_cooldown_minutes * 60:
                return False
                
            msg = MIMEMultipart()
            msg['From'] = EMAIL_CONFIG['sender_email']
            msg['To'] = ', '.join(EMAIL_CONFIG['recipients'])
            msg['Subject'] = f"NIFTY Alert: {subject}"
            
            full_body = f"Alert Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n{body}"
            msg.attach(MIMEText(full_body, 'plain'))
            
            server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
            server.starttls()
            server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
            server.send_message(msg)
            server.quit()
            
            self.last_alert_time = current_time
            print("Alert email sent successfully!")
            return True
            
        except Exception as e:
            print(f"Failed to send email alert: {str(e)}")
            return False
    
    def analyze_market(self):
        try:
            print("\n=== Starting Nifty Analysis ===\n")
            
            handler = TA_Handler(
                symbol="NIFTY",
                exchange="NSE",
                screener="india",
                interval=Interval.INTERVAL_5_MINUTES
            )
            
            print("Fetching market data...")
            analysis = handler.get_analysis()
            
            current_price = analysis.indicators['close']
            rsi = analysis.indicators['RSI']
            macd = analysis.indicators['MACD.macd']
            macd_signal = analysis.indicators['MACD.signal']
            
            # Determine trend and strength
            trend = "neutral"
            strength = 0
            
            # RSI Analysis
            if rsi > 60:
                trend = "bullish"
                strength += 2
            elif rsi < 40:
                trend = "bearish"
                strength += 2
                
            # MACD Analysis
            if macd > macd_signal:
                if trend == "bullish":
                    strength += 2
                elif trend == "neutral":
                    trend = "bullish"
                    strength += 1
            elif macd < macd_signal:
                if trend == "bearish":
                    strength += 2
                elif trend == "neutral":
                    trend = "bearish"
                    strength += 1
            
            # Print analysis
            print(f"\nCurrent Price: ₹{current_price:.2f}")
            print(f"RSI: {rsi:.2f}")
            print(f"MACD: {macd:.2f}")
            print(f"MACD Signal: {macd_signal:.2f}")
            print(f"Overall Trend: {trend.upper()}")
            print(f"Signal Strength: {strength}/4")
            
            # Send alert for strong signals
            if strength >= 3:
                signal_type = "BUY" if trend == "bullish" else "SELL"
                message = [
                    f"=== NIFTY {signal_type} SIGNAL ===",
                    f"\nPrice: ₹{current_price:.2f}",
                    f"Signal Strength: {strength}/4",
                    f"\nIndicators:",
                    f"RSI: {rsi:.2f}",
                    f"MACD: {macd:.2f}",
                    f"\nTargets:",
                    f"Target 1: ₹{current_price * (1.005 if trend == 'bullish' else 0.995):.2f}",
                    f"Target 2: ₹{current_price * (1.01 if trend == 'bullish' else 0.99):.2f}",
                    f"Stop Loss: ₹{current_price * (0.995 if trend == 'bullish' else 1.005):.2f}"
                ]
                self.send_email_alert(f"{signal_type} Signal", "\n".join(message))
            
            print("\nAnalysis complete!")
            
        except Exception as e:
            print(f"\nError during analysis: {str(e)}")

def main():
    analyzer = NiftyAnalyzer()
    analyzer.analyze_market()

if __name__ == "__main__":
    main()
