# Nifty Intraday Trade Plan Generator

A Python application that generates intraday trading plans for Nifty based on multiple data points including institutional flows, option chain data, price action, VWAP, and global market cues.

## Features

- Real-time data collection:
  - Nifty price and volume data
  - Institutional (FII/DII) flow data
  - Option chain analysis
  - Global market indices
  - SGX Nifty

- Technical Analysis:
  - VWAP calculation
  - Trend identification
  - Support/Resistance levels
  - Momentum indicators
  - Candlestick patterns

- Trade Plan Generation:
  - Primary and alternate setups
  - Entry/Exit levels
  - Stop-loss recommendations
  - Risk management rules
  - Pre-trade confirmation checklist

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd tradebot-Nse
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the main script:
```bash
python src/main.py
```

The program will:
1. Collect market data from various sources
2. Perform technical analysis
3. Generate a comprehensive trade plan with:
   - Market bias analysis
   - Primary and alternate trade setups
   - Risk management parameters
   - Confirmation checklist

## Requirements

- Python 3.8+
- Required packages are listed in `requirements.txt`

## Note

This is a tool for educational and research purposes only. Always do your own research and validation before making trading decisions. The trade plans generated should be used as one of many inputs in your decision-making process.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

MIT License
