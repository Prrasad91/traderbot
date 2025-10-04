from datetime import datetime, time

class TradePlanGenerator:
    def __init__(self):
        self.risk_per_trade = 0.01  # 1% risk per trade
        self.min_rr_ratio = 1.5     # Minimum risk-reward ratio
    
    def generate_trade_plan(self, market_data, technical_data, institutional_data, option_data, global_data):
        if market_data is None or len(market_data) == 0:
            raise ValueError("No market data available")
        
        current_price = market_data['Close'].iloc[-1]
        
        # Analyze all data points to determine market bias
        market_bias = self._determine_market_bias(
            technical_data,
            institutional_data,
            option_data,
            global_data
        )
        
        # Generate trading setups
        setups = self._generate_setups(
            current_price,
            technical_data,
            market_bias
        )
        
        # Define risk management rules
        risk_management = {
            'max_trades': 2,
            'stop_loss_percent': 0.5,  # 0.5% per trade
            'square_off_time': '15:15'  # 3:15 PM
        }
        
        # Create confirmation checklist
        confirmation_checklist = [
            "Price aligned with primary trend",
            "Volume confirming price action",
            "RSI showing momentum in trade direction",
            "No major news events expected",
            "Risk-reward ratio > 1.5",
            "Position size within risk limits"
        ]
        
        return {
            'market_bias': market_bias,
            'setups': setups,
            'risk_management': risk_management,
            'confirmation_checklist': confirmation_checklist
        }
    
    def _determine_market_bias(self, technical_data, institutional_data, option_data, global_data):
        bias = {
            'primary': 'neutral',
            'intraday': 'neutral',
            'confidence': 'low'
        }
        
        # Technical bias
        if technical_data['trend']['trend'] != 'neutral':
            bias['primary'] = technical_data['trend']['trend']
            if technical_data['trend']['strength'] >= 3:
                bias['confidence'] = 'high'
            elif technical_data['trend']['strength'] >= 2:
                bias['confidence'] = 'medium'
        
        # Intraday bias based on multiple factors
        intraday_score = 0
        
        # Technical factors
        if technical_data['momentum']['momentum'] == bias['primary']:
            intraday_score += 1
        
        # Institutional activity
        fii_net = institutional_data['FII']['buy'] - institutional_data['FII']['sell']
        dii_net = institutional_data['DII']['buy'] - institutional_data['DII']['sell']
        if fii_net > 0 and dii_net > 0:
            intraday_score += 1
            if bias['primary'] == 'neutral':
                bias['primary'] = 'bullish'
        elif fii_net < 0 and dii_net < 0:
            intraday_score -= 1
            if bias['primary'] == 'neutral':
                bias['primary'] = 'bearish'
        
        # Options data
        if option_data['PCR'] > 1:  # Put-Call Ratio
            intraday_score += 1
        elif option_data['PCR'] < 0.7:
            intraday_score -= 1
        
        # Global markets influence
        global_sentiment = sum([idx['change'] for idx in global_data.values()])
        if global_sentiment > 0.5:
            intraday_score += 1
        elif global_sentiment < -0.5:
            intraday_score -= 1
        
        # Set intraday bias based on score
        if intraday_score >= 2:
            bias['intraday'] = 'bullish'
        elif intraday_score <= -2:
            bias['intraday'] = 'bearish'
        
        return bias
    
    def _generate_setups(self, current_price, technical_data, market_bias):
        setups = {
            'primary': None,
            'alternate': None
        }
        
        # Primary setup based on main trend
        if market_bias['primary'] != 'neutral':
            key_levels = technical_data['key_levels']
            
            if market_bias['primary'] == 'bullish':
                entry = key_levels['support_1']
                stop_loss = key_levels['support_2']
                target = current_price + (current_price - stop_loss) * self.min_rr_ratio
                
                setups['primary'] = {
                    'type': 'long',
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'target': target,
                    'confirmation': 'Break above recent high with volume'
                }
                
                # Alternate bearish setup if primary is bullish
                setups['alternate'] = {
                    'type': 'short',
                    'entry': key_levels['resistance_2'],
                    'stop_loss': key_levels['resistance_2'] * 1.001,  # 0.1% above
                    'target': current_price - (key_levels['resistance_2'] * 1.001 - current_price) * self.min_rr_ratio,
                    'confirmation': 'Rejection at resistance with high volume'
                }
                
            else:  # Bearish
                entry = key_levels['resistance_1']
                stop_loss = key_levels['resistance_2']
                target = current_price - (stop_loss - current_price) * self.min_rr_ratio
                
                setups['primary'] = {
                    'type': 'short',
                    'entry': entry,
                    'stop_loss': stop_loss,
                    'target': target,
                    'confirmation': 'Break below recent low with volume'
                }
                
                # Alternate bullish setup if primary is bearish
                setups['alternate'] = {
                    'type': 'long',
                    'entry': key_levels['support_2'],
                    'stop_loss': key_levels['support_2'] * 0.999,  # 0.1% below
                    'target': current_price + (current_price - key_levels['support_2'] * 0.999) * self.min_rr_ratio,
                    'confirmation': 'Bounce from support with high volume'
                }
        
        return setups
