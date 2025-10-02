class TradePlanGenerator:
    def __init__(self):
        self.max_trades_per_day = 2
        self.stop_loss_percent = 0.5  # 0.5% of capital
        self.square_off_time = "15:15"  # 3:15 PM
        
    def generate_trade_plan(self, market_data, technical_data, institutional_data, option_data, global_data):
        """Generate a comprehensive trade plan based on all available data"""
        
        # Analyze institutional bias
        inst_bias = self._analyze_institutional_bias(institutional_data)
        
        # Analyze option chain
        option_bias = self._analyze_option_chain(option_data)
        
        # Analyze global cues
        global_bias = self._analyze_global_cues(global_data)
        
        # Combine all analysis for final bias
        overall_bias = self._determine_overall_bias(inst_bias, option_bias, global_bias)
        
        # Generate trade setups
        primary_setup = self._generate_primary_setup(overall_bias, market_data, technical_data)
        alternate_setup = self._generate_alternate_setup(overall_bias, market_data, technical_data)
        
        return {
            "market_bias": {
                "institutional": inst_bias,
                "options": option_bias,
                "global": global_bias,
                "overall": overall_bias
            },
            "setups": {
                "primary": primary_setup,
                "alternate": alternate_setup
            },
            "risk_management": {
                "max_trades": self.max_trades_per_day,
                "stop_loss_percent": self.stop_loss_percent,
                "square_off_time": self.square_off_time
            },
            "confirmation_checklist": self._generate_confirmation_checklist()
        }
    
    def _analyze_institutional_bias(self, institutional_data):
        """Analyze FII/DII data to determine institutional bias"""
        if not institutional_data:
            return "neutral"
            
        fii = institutional_data.get('FII', {})
        dii = institutional_data.get('DII', {})
        
        # Simple logic - can be enhanced
        fii_net = fii.get('cash_flow', 0) + fii.get('futures_oi', 0)
        dii_net = dii.get('cash_flow', 0)
        
        if fii_net > 0 and dii_net > 0:
            return "strongly_bullish"
        elif fii_net > 0:
            return "moderately_bullish"
        elif fii_net < 0 and dii_net < 0:
            return "strongly_bearish"
        elif fii_net < 0:
            return "moderately_bearish"
        return "neutral"
    
    def _analyze_option_chain(self, option_data):
        """Analyze option chain data for bias"""
        if not option_data:
            return "neutral"
            
        pcr = option_data.get('pcr', 0)
        
        if pcr > 1.5:
            return "bullish"
        elif pcr < 0.7:
            return "bearish"
        return "neutral"
    
    def _analyze_global_cues(self, global_data):
        """Analyze global market cues"""
        if not global_data:
            return "neutral"
            
        positive_count = 0
        negative_count = 0
        
        for index_data in global_data.values():
            if index_data.get('change_percent', 0) > 0:
                positive_count += 1
            else:
                negative_count += 1
        
        if positive_count > negative_count:
            return "bullish"
        elif negative_count > positive_count:
            return "bearish"
        return "neutral"
    
    def _determine_overall_bias(self, inst_bias, option_bias, global_bias):
        """Combine all biases to determine overall market bias"""
        bias_map = {
            "strongly_bullish": 2,
            "moderately_bullish": 1,
            "bullish": 1,
            "neutral": 0,
            "moderately_bearish": -1,
            "bearish": -1,
            "strongly_bearish": -2
        }
        
        total_score = (bias_map.get(inst_bias, 0) * 2 +  # Give more weight to institutional bias
                      bias_map.get(option_bias, 0) +
                      bias_map.get(global_bias, 0))
        
        if total_score >= 2:
            return "bullish"
        elif total_score <= -2:
            return "bearish"
        return "neutral"
    
    def _generate_primary_setup(self, bias, market_data, technical_data):
        """Generate primary trading setup based on bias"""
        if market_data is None or technical_data is None:
            return None
            
        vwap = technical_data.get('vwap')
        key_levels = technical_data.get('key_levels', {})
        
        if bias == "bullish":
            return {
                "type": "long",
                "entry": f"Above {key_levels.get('prev_close')} with volume confirmation",
                "stop_loss": key_levels.get('low'),
                "target": key_levels.get('high'),
                "confirmation": "Price above VWAP"
            }
        elif bias == "bearish":
            return {
                "type": "short",
                "entry": f"Below {key_levels.get('prev_close')} with volume confirmation",
                "stop_loss": key_levels.get('high'),
                "target": key_levels.get('low'),
                "confirmation": "Price below VWAP"
            }
        return None
    
    def _generate_alternate_setup(self, bias, market_data, technical_data):
        """Generate alternate trading setup based on bias"""
        if market_data is None or technical_data is None:
            return None
            
        # Alternate setup is usually in the opposite direction of primary
        key_levels = technical_data.get('key_levels', {})
        
        if bias == "bullish":
            return {
                "type": "short",
                "entry": f"Below {key_levels.get('low')} with heavy selling pressure",
                "stop_loss": key_levels.get('vwap'),
                "target": f"{key_levels.get('low')} - 0.5%",
                "confirmation": "Break of support with volume"
            }
        elif bias == "bearish":
            return {
                "type": "long",
                "entry": f"Above {key_levels.get('high')} with heavy buying pressure",
                "stop_loss": key_levels.get('vwap'),
                "target": f"{key_levels.get('high')} + 0.5%",
                "confirmation": "Break of resistance with volume"
            }
        return None
    
    def _generate_confirmation_checklist(self):
        """Generate a checklist for trade confirmation"""
        return [
            "VWAP alignment with trade direction",
            "Volume confirmation",
            "Candlestick pattern confirmation",
            "No contradicting institutional flow",
            "Risk-reward ratio > 1:1",
            "Not too close to day's high/low",
            "Market breadth supporting the move",
            "Time of day appropriate for trade"
        ]
