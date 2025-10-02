import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import json
from nsepython import *

class MarketDataCollector:
    def __init__(self):
        print("Initializing MarketDataCollector...")
        self.nifty_symbol = "NIFTY 50"
        self.use_simulation = True  # For demonstration
        print("Using simulation mode for data collection")
        
    def _get_simulated_nifty_data(self):
        """Get simulated Nifty data for demonstration"""
        return pd.DataFrame({
            'Open': [19500],
            'High': [19600],
            'Low': [19400],
            'Close': [19550],
            'Volume': [1000000],
            'Prev Close': [19480]
        }, index=[pd.Timestamp.now()])
        
    def _get_simulated_institutional_data(self):
        """Get simulated institutional data"""
        return {
            "FII": {
                "cash_flow": 1250.5,
                "futures_oi": 850.75,
                "options_oi": 1500.25
            },
            "DII": {
                "cash_flow": 750.25,
                "futures_oi": 0,
                "options_oi": 0
            }
        }
        
    def _get_simulated_option_chain(self):
        """Get simulated option chain data"""
        current_price = 19550
        strikes = range(int(current_price - 500), int(current_price + 500), 100)
        
        calls = []
        puts = []
        total_call_oi = 0
        total_put_oi = 0
        
        for strike in strikes:
            # More OI around ATM strikes
            distance = abs(strike - current_price)
            base_oi = max(10000 - distance, 1000)
            
            call_oi = base_oi + np.random.randint(-500, 500)
            put_oi = base_oi + np.random.randint(-500, 500)
            
            calls.append({
                "strike": strike,
                "oi": call_oi,
                "change_oi": np.random.randint(-200, 200)
            })
            puts.append({
                "strike": strike,
                "oi": put_oi,
                "change_oi": np.random.randint(-200, 200)
            })
            
            total_call_oi += call_oi
            total_put_oi += put_oi
        
        return {
            "calls": calls,
            "puts": puts,
            "pcr": round(total_put_oi / total_call_oi, 2)
        }
        
    def _get_simulated_indices(self):
        """Get simulated indices data"""
        return {
            'NIFTY 50': {
                "price": 19550.25,
                "change": 125.75,
                "change_percent": 0.65
            },
            'NIFTY BANK': {
                "price": 44250.50,
                "change": 350.25,
                "change_percent": 0.80
            },
            'INDIA VIX': {
                "price": 12.75,
                "change": -0.50,
                "change_percent": -3.77
            },
            'NIFTY NEXT 50': {
                "price": 45750.25,
                "change": 225.50,
                "change_percent": 0.50
            }
        }
        
    def get_nifty_data(self):
        """Get current Nifty data including OHLCV"""
        try:
            if self.use_simulation:
                return self._get_simulated_nifty_data()
                
            print("Fetching Nifty data...")
            nifty_data = nse_quote_meta("NIFTY 50", "latest")
            
            df = pd.DataFrame({
                'Open': [float(nifty_data.get('open', 0))],
                'High': [float(nifty_data.get('dayHigh', 0))],
                'Low': [float(nifty_data.get('dayLow', 0))],
                'Close': [float(nifty_data.get('lastPrice', 0))],
                'Volume': [int(nifty_data.get('totalTradedVolume', 0))],
                'Prev Close': [float(nifty_data.get('previousClose', 0))]
            }, index=[pd.Timestamp.now()])
            
            print(f"Data shape: {df.shape}")
            return df
            
        except Exception as e:
            print(f"Error fetching Nifty data: {e}")
            return self._get_simulated_nifty_data()
            
    def get_institutional_data(self):
        """Get FII/DII data"""
        try:
            if self.use_simulation:
                return self._get_simulated_institutional_data()
                
            print("Fetching institutional data...")
            fii_data = nse_fii_dii()
            
            if not fii_data:
                raise Exception("No institutional data available")
                
            return {
                "FII": {
                    "cash_flow": float(fii_data.get('FII/FPI', {}).get('Cash', 0)),
                    "futures_oi": float(fii_data.get('FII/FPI', {}).get('Index Futures', 0)),
                    "options_oi": float(fii_data.get('FII/FPI', {}).get('Index Options', 0))
                },
                "DII": {
                    "cash_flow": float(fii_data.get('DII', {}).get('Cash', 0)),
                    "futures_oi": 0,
                    "options_oi": 0
                }
            }
            
        except Exception as e:
            print(f"Error fetching institutional data: {e}")
            return self._get_simulated_institutional_data()
            
    def get_option_chain(self):
        """Get Nifty option chain data"""
        try:
            if self.use_simulation:
                return self._get_simulated_option_chain()
                
            print("Fetching option chain data...")
            chain = nse_optionchain_scrapper("NIFTY")
            
            if not chain:
                raise Exception("No option chain data available")
            
            calls = []
            puts = []
            total_call_oi = 0
            total_put_oi = 0
            
            for record in chain['records']['data']:
                if 'CE' in record:
                    ce = record['CE']
                    calls.append({
                        "strike": ce.get('strikePrice', 0),
                        "oi": ce.get('openInterest', 0),
                        "change_oi": ce.get('changeinOpenInterest', 0)
                    })
                    total_call_oi += ce.get('openInterest', 0)
                    
                if 'PE' in record:
                    pe = record['PE']
                    puts.append({
                        "strike": pe.get('strikePrice', 0),
                        "oi": pe.get('openInterest', 0),
                        "change_oi": pe.get('changeinOpenInterest', 0)
                    })
                    total_put_oi += pe.get('openInterest', 0)
            
            pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 0
            
            return {
                "calls": sorted(calls, key=lambda x: x['strike']),
                "puts": sorted(puts, key=lambda x: x['strike']),
                "pcr": round(pcr, 2)
            }
            
        except Exception as e:
            print(f"Error fetching option chain: {e}")
            return self._get_simulated_option_chain()
            
    def get_global_indices(self):
        """Get indices data"""
        try:
            if self.use_simulation:
                return self._get_simulated_indices()
                
            print("Fetching indices data...")
            all_indices = nse_get_indices()
            
            if not all_indices:
                raise Exception("No indices data available")
            
            indices_of_interest = ['NIFTY 50', 'NIFTY BANK', 'INDIA VIX', 'NIFTY NEXT 50']
            result = {}
            
            for index in all_indices:
                if index['indexSymbol'] in indices_of_interest:
                    result[index['indexSymbol']] = {
                        "price": float(index.get('last', 0)),
                        "change": float(index.get('change', 0)),
                        "change_percent": float(index.get('pChange', 0))
                    }
            
            return result
            
        except Exception as e:
            print(f"Error fetching indices data: {e}")
            return self._get_simulated_indices()
