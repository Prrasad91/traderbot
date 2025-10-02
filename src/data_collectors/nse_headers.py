"""NSE headers and constants for data collection"""

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'X-Requested-With': 'XMLHttpRequest',
    'Pragma': 'no-cache',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1'
}

# NSE URLs
BASE_URL = "https://www.nseindia.com"
OPTION_CHAIN_URL = f"{BASE_URL}/option-chain"
FII_DII_URL = f"{BASE_URL}/api/marketStatus"
MARKET_STATUS_URL = f"{BASE_URL}/api/marketStatus"
NIFTY_QUOTE_URL = f"{BASE_URL}/api/equity-stockIndices?index=NIFTY%2050"
OPTION_CHAIN_API = f"{BASE_URL}/api/option-chain-indices?symbol=NIFTY"

# Cookie URL to get required cookies
COOKIE_URL = f"{BASE_URL}/get-quotes/equity?symbol=NIFTY"

# Market timings
MARKET_OPEN = "09:15"
MARKET_CLOSE = "15:30"
