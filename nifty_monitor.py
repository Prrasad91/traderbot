"""Real-time trading system with alerts and visualization"""
import pandas as pd
import numpy as np
import requests
import json
import os
import winsound
from datetime import datetime, timedelta
from time import sleep
from tradingview_ta import TA_Handler, Interval, Exchange
from threading import Thread
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class TradingViewSession:
    def __init__(self):
        self.handler = TA_Handler(
            symbol="NIFTY",
            exchange="NSE",
            screener="india",
            interval=Interval.INTERVAL_5_MINUTES,
            timeout=30
        )
        self.handlers = {
            "5m": self.handler,
            "15m": TA_Handler(
                symbol="NIFTY",
                exchange="NSE",
                screener="india",
                interval=Interval.INTERVAL_15_MINUTES,
                timeout=30
            ),
            "1h": TA_Handler(
                symbol="NIFTY",
                exchange="NSE",
                screener="india",
                interval=Interval.INTERVAL_1_HOUR,
                timeout=30
            )
        }
        self.data_history = {tf: [] for tf in self.handlers.keys()}
        self.max_history = 100

    def get_analysis(self):
        """Get technical analysis data from TradingView"""
        try:
            data = {}
            for timeframe, handler in self.handlers.items():
                try:
                    analysis = handler.get_analysis()
                    indicators = analysis.indicators
                    oscillators = analysis.oscillators
                    moving_averages = analysis.moving_averages
                    
                    timeframe_data = {
                        'timestamp': datetime.now(),
                        'close': indicators.get('close', 0),
                        'open': indicators.get('open', 0),
                        'high': indicators.get('high', 0),
                        'low': indicators.get('low', 0),
                        'volume': indicators.get('volume', 0),
                        'RSI': indicators.get('RSI', 0),
                        'RSI[1]': indicators.get('RSI[1]', 0),
                        'EMA20': indicators.get('EMA20', 0),
                        'EMA50': indicators.get('EMA50', 0),
                        'EMA200': indicators.get('EMA200', 0),
                        'BB.upper': indicators.get('BB.upper', 0),
                        'BB.lower': indicators.get('BB.lower', 0),
                        'BB.middle': indicators.get('BB.middle', 0),
                        'MACD.macd': indicators.get('MACD.macd', 0),
                        'MACD.signal': indicators.get('MACD.signal', 0),
                        'ADX': indicators.get('ADX', 0),
                        'ADX+': indicators.get('ADX+DI', 0),
                        'ADX-': indicators.get('ADX-DI', 0),
                        'Stoch.K': indicators.get('Stoch.K', 0),
                        'Stoch.D': indicators.get('Stoch.D', 0),
                        'ATR': indicators.get('ATR', 0),
                        'recommendation': analysis.summary.get('RECOMMENDATION', 'NEUTRAL'),
                        'oscillator_summary': oscillators.get('RECOMMENDATION', 'NEUTRAL'),
                        'ma_summary': moving_averages.get('RECOMMENDATION', 'NEUTRAL')
                    }
                    
                    # Add to history
                    self.data_history[timeframe].append(timeframe_data)
                    if len(self.data_history[timeframe]) > self.max_history:
                        self.data_history[timeframe].pop(0)
                    
                    data[timeframe] = timeframe_data
                    
                except Exception as e:
                    print(f"Error getting {timeframe} analysis: {str(e)}")
                    continue
            
            return data
        except Exception as e:
            print(f"Error in get_analysis: {str(e)}")
            return None

class TradingSystem:
    def __init__(self):
        self.tv_session = TradingViewSession()
        self.last_data = None
        self.risk_per_trade = 0.01
        self.min_rr_ratio = 1.5
        self.last_alert_time = None
        self.alert_cooldown = timedelta(minutes=5)
        self.monitoring = False
        self.monitor_thread = None
        self.charts_dir = "charts"
        
        if not os.path.exists(self.charts_dir):
            os.makedirs(self.charts_dir)

    def generate_chart(self, tv_data, timeframe='5m'):
        """Generate an interactive chart with indicators"""
        try:
            history = self.tv_session.data_history[timeframe]
            if not history:
                return
            
            # Create figure with secondary y-axis
            fig = make_subplots(rows=3, cols=1, 
                              shared_xaxes=True,
                              vertical_spacing=0.05,
                              row_heights=[0.6, 0.2, 0.2])

            # Add candlestick
            df = pd.DataFrame(history)
            fig.add_trace(go.Candlestick(
                x=df['timestamp'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='Price'
            ), row=1, col=1)

            # Add EMAs
            fig.add_trace(go.Scatter(x=df['timestamp'], y=df['EMA20'], name='EMA20', line=dict(color='blue')), row=1, col=1)
            fig.add_trace(go.Scatter(x=df['timestamp'], y=df['EMA50'], name='EMA50', line=dict(color='orange')), row=1, col=1)
            fig.add_trace(go.Scatter(x=df['timestamp'], y=df['EMA200'], name='EMA200', line=dict(color='red')), row=1, col=1)

            # Add Bollinger Bands
            fig.add_trace(go.Scatter(x=df['timestamp'], y=df['BB.upper'], name='BB Upper', line=dict(color='gray', dash='dash')), row=1, col=1)
            fig.add_trace(go.Scatter(x=df['timestamp'], y=df['BB.lower'], name='BB Lower', line=dict(color='gray', dash='dash')), row=1, col=1)

            # Add RSI
            fig.add_trace(go.Scatter(x=df['timestamp'], y=df['RSI'], name='RSI', line=dict(color='purple')), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

            # Add MACD
            fig.add_trace(go.Scatter(x=df['timestamp'], y=df['MACD.macd'], name='MACD', line=dict(color='blue')), row=3, col=1)
            fig.add_trace(go.Scatter(x=df['timestamp'], y=df['MACD.signal'], name='Signal', line=dict(color='orange')), row=3, col=1)

            # Update layout
            fig.update_layout(
                title=f'Nifty Analysis ({timeframe})',
                yaxis_title='Price',
                yaxis2_title='RSI',
                yaxis3_title='MACD',
                xaxis_rangeslider_visible=False
            )

            # Save chart
            filename = f"nifty_chart_{timeframe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            fig.write_html(os.path.join(self.charts_dir, filename))
            return filename

        except Exception as e:
            print(f"Error generating chart: {str(e)}")
            return None

    def play_alert(self, bullish=True):
        """Play sound alert"""
        try:
            freq = 1000 if bullish else 500
            duration = 500
            winsound.Beep(freq, duration)
        except:
            print("\a")  # Fallback to system beep

    def check_signals(self, tv_data):
        """Check for trading signals"""
        if not tv_data or '5m' not in tv_data:
            return None
            
        data_5m = tv_data['5m']
        signals = []
        
        # RSI signals
        if data_5m['RSI'] < 30 and data_5m['RSI'] > data_5m.get('RSI[1]', 0):
            signals.append(("BULLISH", "RSI oversold with positive momentum"))
        elif data_5m['RSI'] > 70 and data_5m['RSI'] < data_5m.get('RSI[1]', 0):
            signals.append(("BEARISH", "RSI overbought with negative momentum"))
            
        # MACD crossover
        if data_5m['MACD.macd'] > data_5m['MACD.signal'] and \
           data_5m.get('MACD.macd', 0) <= data_5m.get('MACD.signal', 0):
            signals.append(("BULLISH", "MACD bullish crossover"))
        elif data_5m['MACD.macd'] < data_5m['MACD.signal'] and \
             data_5m.get('MACD.macd', 0) >= data_5m.get('MACD.signal', 0):
            signals.append(("BEARISH", "MACD bearish crossover"))
            
        # Bollinger Bands
        current_price = data_5m['close']
        if current_price <= data_5m['BB.lower']:
            signals.append(("BULLISH", "Price at lower Bollinger Band"))
        elif current_price >= data_5m['BB.upper']:
            signals.append(("BEARISH", "Price at upper Bollinger Band"))
            
        # Trend following
        if current_price > data_5m['EMA20'] > data_5m['EMA50'] and \
           data_5m['ADX'] > 25 and data_5m['ADX+'] > data_5m['ADX-']:
            signals.append(("BULLISH", "Strong uptrend with ADX confirmation"))
        elif current_price < data_5m['EMA20'] < data_5m['EMA50'] and \
             data_5m['ADX'] > 25 and data_5m['ADX-'] > data_5m['ADX+']:
            signals.append(("BEARISH", "Strong downtrend with ADX confirmation"))
            
        return signals

    def alert_signals(self, signals):
        """Alert user of trading signals"""
        if not signals:
            return
            
        current_time = datetime.now()
        if self.last_alert_time and (current_time - self.last_alert_time) < self.alert_cooldown:
            return
            
        self.last_alert_time = current_time
        
        print("\n=== TRADING SIGNALS DETECTED ===")
        print(f"Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        for bias, reason in signals:
            print(f"{bias}: {reason}")
            self.play_alert(bias == "BULLISH")

    def monitor_market(self):
        """Continuously monitor market for signals"""
        while self.monitoring:
            try:
                # Get fresh data
                tv_data = self.tv_session.get_analysis()
                if tv_data:
                    # Check for signals
                    signals = self.check_signals(tv_data)
                    if signals:
                        self.alert_signals(signals)
                        # Generate new chart
                        self.generate_chart(tv_data)
                    
                    # Update last data
                    self.last_data = tv_data
                    
                # Wait before next check
                sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Error in market monitor: {str(e)}")
                sleep(5)

    def start_monitoring(self):
        """Start market monitoring in a separate thread"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = Thread(target=self.monitor_market)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            print("Market monitoring started")
            return True
        return False

    def stop_monitoring(self):
        """Stop market monitoring"""
        if self.monitoring:
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join()
            print("Market monitoring stopped")
            return True
        return False

if __name__ == "__main__":
    try:
        system = TradingSystem()
        print("Starting market monitoring...")
        system.start_monitoring()
        
        print("\nPress Ctrl+C to stop monitoring")
        while True:
            sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping market monitoring...")
        system.stop_monitoring()
        print("System shutdown complete")
