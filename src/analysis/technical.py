import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .. import config
from scipy.stats import norm
from sklearn.cluster import KMeans
import requests
import json
import openai

__all__ = ['TechnicalAnalyzer']

# Email configuration
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'sriram86rs@gmail.com',  # Your Gmail
    'sender_password': 'rlcd rmyu zshb eajy',   # Your Gmail App Password
    'recipients': ['venkateshprasad.s@hotmail.com']  # Single recipient for major signals
}

class TechnicalAnalyzer:
    def __init__(self):
        self.vwap_period = 20
        self.intervals = config.INTERVALS  # ["5m", "15m", "1h"]
        self.weights = {"5m": 0.5, "15m": 0.3, "1h": 0.2}  # Weight by importance
        self.last_alert_time = None
        self.alert_cooldown_minutes = 30  # Minimum time between alerts
        self.nse_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
    def fetch_nifty_data(self, interval='1d', period='1mo'):
        """
        Fetch NIFTY 50 data using yfinance
        interval: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        period: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,max
        """
        try:
            # Fetch from Yahoo Finance
            nifty = yf.Ticker("^NSEI")
            df = nifty.history(period=period, interval=interval)
            
            if df.empty:
                return None
                
            return df
            
        except Exception as e:
            print(f"Error fetching NIFTY data: {str(e)}")
            return None
            
    def fetch_nse_market_status(self):
        """Fetch current NSE market status"""
        try:
            url = "https://www.nseindia.com/api/marketStatus"
            response = requests.get(url, headers=self.nse_headers, timeout=5)
            data = response.json()
            return {
                'market_status': data['marketState'][0]['marketStatus'],
                'last_update': data['marketState'][0]['lastUpdateTime']
            }
        except Exception as e:
            print(f"Error fetching market status: {str(e)}")
            return None
            
    def fetch_nse_india_vix(self):
        """Fetch current India VIX value"""
        try:
            url = "https://www.nseindia.com/api/marketStatus"
            response = requests.get(url, headers=self.nse_headers, timeout=5)
            data = response.json()
            vix_data = next((item for item in data['marketState'] if item['index'] == 'INDIA VIX'), None)
            if vix_data:
                return {
                    'value': float(vix_data['last']),
                    'change': float(vix_data['variation']),
                    'last_update': vix_data['lastUpdateTime']
                }
            return None
        except Exception as e:
            print(f"Error fetching India VIX: {str(e)}")
            return None
            
    def get_market_depth(self, symbol="NIFTY 50"):
        """Get market depth data for the specified symbol"""
        try:
            url = f"https://www.nseindia.com/api/depth-data?symbol={symbol}"
            response = requests.get(url, headers=self.nse_headers, timeout=5)
            return response.json()
        except Exception as e:
            print(f"Error fetching market depth: {str(e)}")
            return None
            
    def calculate_market_sentiment(self, data):
        """Calculate market sentiment based on various indicators"""
        if data is None or len(data) == 0:
            return None
            
        try:
            # Get recent price action
            recent_data = data.tail(20)  # Last 20 periods
            price_change = recent_data['Close'].pct_change()
            volume_change = recent_data['Volume'].pct_change()
            
            # Calculate basic sentiment indicators
            sentiment = {
                'price_trend': 'up' if price_change.mean() > 0 else 'down',
                'volume_trend': 'up' if volume_change.mean() > 0 else 'down',
                'volatility': price_change.std() * 100,  # Convert to percentage
                'strength': 0  # Base strength
            }
            
            # Add strength based on price and volume alignment
            if sentiment['price_trend'] == sentiment['volume_trend']:
                sentiment['strength'] += 1
                
            # Add strength based on volatility
            if sentiment['volatility'] < price_change.std() * 100:  # Compare to historical volatility
                sentiment['strength'] += 1
                
            # Get VIX data if available
            vix_data = self.fetch_nse_india_vix()
            if vix_data:
                sentiment['vix'] = vix_data['value']
                sentiment['vix_change'] = vix_data['change']
                
                # Add VIX-based sentiment
                if vix_data['value'] < 15:  # Low volatility
                    sentiment['volatility_regime'] = 'low'
                    sentiment['strength'] += 1
                elif vix_data['value'] > 25:  # High volatility
                    sentiment['volatility_regime'] = 'high'
                    sentiment['strength'] -= 1
                else:
                    sentiment['volatility_regime'] = 'normal'
                    
            return sentiment
            
        except Exception as e:
            print(f"Error calculating market sentiment: {str(e)}")
            return None
        
    def send_email_alert(self, subject, body):
        """Send email alerts to configured recipients"""
        try:
            current_time = datetime.now()
            
            # Check cooldown period
            if self.last_alert_time and (current_time - self.last_alert_time).total_seconds() < self.alert_cooldown_minutes * 60:
                return False
                
            msg = MIMEMultipart()
            msg['From'] = EMAIL_CONFIG['sender_email']
            msg['To'] = ', '.join(EMAIL_CONFIG['recipients'])
            msg['Subject'] = f"NIFTY Trading Alert: {subject}"
            
            # Add timestamp to body
            full_body = f"Alert Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n{body}"
            msg.attach(MIMEText(full_body, 'plain'))
            
            # Connect to SMTP server
            server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
            server.starttls()
            server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            self.last_alert_time = current_time
            return True
            
        except Exception as e:
            print(f"Failed to send email alert: {str(e)}")
            return False
            
    def generate_alert_message(self, analysis_data, current_price):
        """Generate focused buy/sell alert message with detailed recommendations"""
        message = []
        message.append("=== NIFTY MAJOR TRADING SIGNAL ===")
        message.append(f"\nCurrent Price: ₹{current_price:.2f}")
        
        # Determine signal type and strength
        trend = analysis_data['trend']['trend']
        trend_strength = analysis_data['trend']['strength']
        momentum = analysis_data['momentum']['momentum']
        
        # Add trading signal with clear action
        signal_type = None
        if (trend == 'bullish' and momentum == 'bullish' and trend_strength >= 4):
            signal_type = "STRONG BUY"
        elif (trend == 'bearish' and momentum == 'bearish' and trend_strength >= 4):
            signal_type = "STRONG SELL"
            
        if signal_type:
            message.append(f"\nSIGNAL: {signal_type}")
            
            # Add key price levels for trade management
            levels = analysis_data['levels']
            if signal_type == "STRONG BUY":
                message.append(f"Target 1: ₹{levels['resistance_1']}")
                message.append(f"Target 2: ₹{levels['resistance_2']}")
                message.append(f"Stop Loss: ₹{levels['support_2']}")
                
                # Trading recommendations for bullish setup
                message.append("\nRECOMMENDED TRADES:")
                atm_strike = round(current_price / 50) * 50  # Round to nearest 50
                message.append("1. Index Trade:")
                message.append(f"   - Buy NIFTY Futures with strict stop loss")
                message.append("\n2. Options Strategy (Conservative):")
                message.append(f"   - Buy {atm_strike} Call")
                message.append(f"   - Sell {atm_strike + 200} Call (Bear Spread)")
                message.append("\n3. Options Strategy (Aggressive):")
                message.append(f"   - Buy {atm_strike} Call")
                message.append(f"   - Target: 50-70% profit")
                message.append(f"   - Stop Loss: 30% of premium")
                
            else:  # STRONG SELL
                message.append(f"Target 1: ₹{levels['support_1']}")
                message.append(f"Target 2: ₹{levels['support_2']}")
                message.append(f"Stop Loss: ₹{levels['resistance_2']}")
                
                # Trading recommendations for bearish setup
                message.append("\nRECOMMENDED TRADES:")
                atm_strike = round(current_price / 50) * 50  # Round to nearest 50
                message.append("1. Index Trade:")
                message.append(f"   - Sell NIFTY Futures with strict stop loss")
                message.append("\n2. Options Strategy (Conservative):")
                message.append(f"   - Buy {atm_strike} Put")
                message.append(f"   - Sell {atm_strike - 200} Put (Bull Spread)")
                message.append("\n3. Options Strategy (Aggressive):")
                message.append(f"   - Buy {atm_strike} Put")
                message.append(f"   - Target: 50-70% profit")
                message.append(f"   - Stop Loss: 30% of premium")
            
            # Position sizing recommendations
            message.append("\nPOSITION SIZING:")
            risk_points = abs(current_price - (levels['support_2'] if signal_type == "STRONG BUY" else levels['resistance_2']))
            message.append(f"- Risk per trade: Maximum 1-2% of capital")
            message.append(f"- Points at risk: {risk_points:.2f}")
            message.append(f"- For ₹1,00,000 capital (example):")
            message.append(f"  * Max risk: ₹2,000")
            message.append(f"  * Lot size: According to risk per point")
                
            # Add confirmation factors
            message.append("\nCONFIRMATION FACTORS:")
            if analysis_data['patterns']:
                message.append(f"- Candlestick Pattern: {', '.join(analysis_data['patterns'])}")
            if trend_strength >= 4:
                message.append(f"- Strong {trend.upper()} trend (Strength: {trend_strength}/5)")
            
            # Risk warning
            message.append("\nRISK MANAGEMENT RULES:")
            message.append("1. Always use stop loss - No exceptions")
            message.append("2. Don't risk more than 2% of capital per trade")
            message.append("3. Exit half position at Target 1")
            message.append("4. Trail stop loss after Target 1 is hit")
            message.append("5. Book profits at end of day if targets not hit")
            
        return "\n".join(message)
    
    def calculate_vwap(self, data):
        if data is None or len(data) == 0:
            return data
            
        df = data.copy()
        df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
        df['VP'] = df['Typical_Price'] * df['Volume']
        df['Cumulative_VP'] = df['VP'].cumsum()
        df['Cumulative_Volume'] = df['Volume'].cumsum()
        df['VWAP'] = df['Cumulative_VP'] / df['Cumulative_Volume']
        return df
    
    def identify_trend(self, data):
        if data is None or len(data) == 0:
            return {'trend': 'neutral', 'strength': 0}
            
        current_price = data['Close'].iloc[-1]
        vwap = data['VWAP'].iloc[-1] if 'VWAP' in data.columns else current_price
        rsi = data['RSI'].iloc[-1]
        adx = data['ADX'].iloc[-1]
        
        trend = 'neutral'
        strength = 0
        
        # Determine trend based on price vs VWAP
        if current_price > vwap:
            trend = 'bullish'
            strength += 1
        elif current_price < vwap:
            trend = 'bearish'
            strength += 1
        
        # Add RSI confirmation
        if rsi > 60:
            if trend == 'bullish':
                strength += 1
        elif rsi < 40:
            if trend == 'bearish':
                strength += 1
        
        # Add ADX strength
        if adx > 25:
            strength += 1
        
        return {
            'trend': trend,
            'strength': min(5, strength)  # Cap strength at 5
        }
    
    def identify_key_levels(self, data):
        if data is None or len(data) == 0:
            return {}
            
        current_price = data['Close'].iloc[-1]
        
        return {
            'support_1': round(current_price * 0.995, 2),
            'support_2': round(current_price * 0.99, 2),
            'resistance_1': round(current_price * 1.005, 2),
            'resistance_2': round(current_price * 1.01, 2)
        }
    
    def validate_momentum(self, data):
        if data is None or len(data) == 0:
            return {'momentum': 'neutral', 'strength': 0}
            
        rsi = data['RSI'].iloc[-1]
        macd = data['MACD'].iloc[-1]
        macd_signal = data['MACD_Signal'].iloc[-1]
        
        momentum = 'neutral'
        strength = 0
        
        # RSI momentum
        if rsi > 60:
            momentum = 'bullish'
            strength += 1
        elif rsi < 40:
            momentum = 'bearish'
            strength += 1
        
        # MACD momentum
        if macd > macd_signal:
            if momentum == 'bullish':
                strength += 1
            elif momentum == 'neutral':
                momentum = 'bullish'
                strength += 1
        elif macd < macd_signal:
            if momentum == 'bearish':
                strength += 1
            elif momentum == 'neutral':
                momentum = 'bearish'
                strength += 1
        
        return {
            'momentum': momentum,
            'strength': min(5, strength)  # Cap strength at 5
        }
    
    def calculate_volume_profile(self, data, num_bins=10):
        """Calculate Volume Profile to identify high-volume price levels"""
        if data is None or len(data) < num_bins:
            return None
            
        price_range = data['High'].max() - data['Low'].min()
        bin_size = price_range / num_bins
        
        volume_profile = []
        current_price = data['Close'].iloc[-1]
        
        for i in range(num_bins):
            price_level = data['Low'].min() + (i * bin_size)
            mask = (data['Low'] >= price_level) & (data['Low'] < price_level + bin_size)
            volume = data.loc[mask, 'Volume'].sum()
            volume_profile.append({
                'price_level': price_level,
                'volume': volume,
                'distance_from_current': abs(price_level - current_price)
            })
        
        # Sort by volume to find POC (Point of Control)
        volume_profile.sort(key=lambda x: x['volume'], reverse=True)
        return volume_profile[:3]  # Return top 3 high-volume levels
    
    def calculate_fibonacci_levels(self, data):
        """Calculate Fibonacci retracement and extension levels"""
        if data is None or len(data) == 0:
            return None
            
        high = data['High'].max()
        low = data['Low'].min()
        price_range = high - low
        current = data['Close'].iloc[-1]
        
        # Fibonacci ratios
        ratios = {
            'Extension 1.618': high + price_range * 0.618,
            'Extension 1.272': high + price_range * 0.272,
            'Resistance 1': high,
            'Retracement 0.618': high - price_range * 0.618,
            'Retracement 0.5': high - price_range * 0.5,
            'Retracement 0.382': high - price_range * 0.382,
            'Support 1': low
        }
        
        return {level: round(price, 2) for level, price in ratios.items()}
    
    def detect_divergence(self, data, window=14):
        """Detect RSI and price divergences"""
        if data is None or len(data) < window:
            return None
            
        df = data.tail(window).copy()
        
        # Find price swings
        price_high = df['Close'].max()
        price_low = df['Close'].min()
        price_trend = 'up' if df['Close'].iloc[-1] > df['Close'].iloc[0] else 'down'
        
        # Find RSI swings
        rsi_high = df['RSI'].max()
        rsi_low = df['RSI'].min()
        rsi_trend = 'up' if df['RSI'].iloc[-1] > df['RSI'].iloc[0] else 'down'
        
        # Check for divergences
        bullish_div = price_trend == 'down' and rsi_trend == 'up'
        bearish_div = price_trend == 'up' and rsi_trend == 'down'
        
        if bullish_div:
            return {'type': 'bullish', 'strength': abs(df['RSI'].iloc[-1] - df['RSI'].iloc[0])}
        elif bearish_div:
            return {'type': 'bearish', 'strength': abs(df['RSI'].iloc[-1] - df['RSI'].iloc[0])}
        
        return None
    
    def identify_support_resistance_clusters(self, data, n_clusters=5):
        """Identify support and resistance levels using price clusters"""
        if data is None or len(data) < n_clusters:
            return None
            
        # Prepare price points for clustering
        price_points = np.column_stack([
            data['High'].values,
            data['Low'].values,
            data['Close'].values
        ])
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        kmeans.fit(price_points)
        
        # Get cluster centers and sort them
        levels = sorted([round(center[2], 2) for center in kmeans.cluster_centers_])
        current_price = data['Close'].iloc[-1]
        
        # Categorize levels as support or resistance
        support_resistance = {'support': [], 'resistance': []}
        for level in levels:
            if level < current_price:
                support_resistance['support'].append(level)
            else:
                support_resistance['resistance'].append(level)
                
        return support_resistance
    
    def calculate_market_profile(self, data, std_dev_range=2):
        """Calculate Market Profile based on normal distribution"""
        if data is None or len(data) == 0:
            return None
            
        mean_price = data['Close'].mean()
        std_price = data['Close'].std()
        
        # Generate value area
        value_area_high = mean_price + (std_dev_range * std_price)
        value_area_low = mean_price - (std_dev_range * std_price)
        
        # Calculate price distribution
        prices = np.linspace(value_area_low, value_area_high, 50)
        distribution = norm.pdf(prices, mean_price, std_price)
        
        return {
            'poc': round(mean_price, 2),  # Point of Control
            'vah': round(value_area_high, 2),  # Value Area High
            'val': round(value_area_low, 2),  # Value Area Low
            'value_area_volume': round(norm.cdf(value_area_high, mean_price, std_price) - 
                                    norm.cdf(value_area_low, mean_price, std_price), 3)
        }
    
    def identify_candlestick_pattern(self, data):
        if data is None or len(data) == 0:
            return None
            
        current = data.iloc[-1]
        prev = data.iloc[-2] if len(data) > 1 else None
        
        body = current['Close'] - current['Open']
        total_range = current['High'] - current['Low']
        upper_wick = current['High'] - max(current['Open'], current['Close'])
        lower_wick = min(current['Open'], current['Close']) - current['Low']
        
        patterns = []
        
        # Enhanced pattern detection
        if abs(body) < 0.2 * total_range and upper_wick > 0.4 * total_range and lower_wick > 0.4 * total_range:
            patterns.append('Doji')
        elif body > 0 and body > 0.7 * total_range and upper_wick < 0.15 * total_range:
            patterns.append('Bullish Marubozu')
        elif body < 0 and abs(body) > 0.7 * total_range and lower_wick < 0.15 * total_range:
            patterns.append('Bearish Marubozu')
            
        # Check for engulfing patterns if we have previous candle
        if prev is not None:
            prev_body = prev['Close'] - prev['Open']
            if body > 0 and prev_body < 0 and current['Open'] < prev['Close'] and current['Close'] > prev['Open']:
                patterns.append('Bullish Engulfing')
            elif body < 0 and prev_body > 0 and current['Open'] > prev['Close'] and current['Close'] < prev['Open']:
                patterns.append('Bearish Engulfing')
        
        return patterns if patterns else None
    
    def check_and_send_alerts(self, data):
        """Check for major buy/sell signals and send focused alerts"""
        if data is None or len(data) == 0:
            return
            
        # Get current price
        current_price = data['Close'].iloc[-1]
            
        # Gather essential analysis data
        analysis_data = {
            'trend': self.identify_trend(data),
            'momentum': self.validate_momentum(data),
            'levels': self.identify_key_levels(data),
            'patterns': self.identify_candlestick_pattern(data),
            'market_sentiment': self.calculate_market_sentiment(data),
            'market_status': self.fetch_nse_market_status(),
            'vix_data': self.fetch_nse_india_vix()
        }
        
        # Check for strong buy/sell signals
        trend = analysis_data['trend']['trend']
        trend_strength = analysis_data['trend']['strength']
        momentum = analysis_data['momentum']['momentum']
        
        # Only alert for very strong signals with clear direction
        should_alert = (
            trend_strength >= 4 and  # Strong trend
            trend == momentum and    # Trend and momentum agree
            trend in ['bullish', 'bearish']  # Clear direction
        )
        
        # Send alert only for major signals
        if should_alert:
            signal_type = "BUY" if trend == 'bullish' else "SELL"
            subject = f"NIFTY MAJOR {signal_type} SIGNAL"
            alert_message = self.generate_alert_message(analysis_data, current_price)
            self.send_email_alert(subject, alert_message)
            
        return analysis_data
