import requests
import time
from functools import wraps
from .nse_headers import HEADERS, BASE_URL, COOKIE_URL

def retry_session(max_retries=3, delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    print(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator

class NSESession:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.cookies = None
        self.last_request_time = 0
        self.min_request_gap = 1  # minimum seconds between requests
        
    def _wait_for_rate_limit(self):
        """Ensure minimum gap between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_gap:
            time.sleep(self.min_request_gap - time_since_last)
        self.last_request_time = time.time()
        
    @retry_session(max_retries=3, delay=2)
    def get_cookies(self):
        """Get fresh cookies from NSE"""
        print("Getting fresh NSE cookies...")
        self.session.get(BASE_URL, timeout=10)
        response = self.session.get(COOKIE_URL, timeout=10)
        self.cookies = response.cookies
        return self.cookies
        
    @retry_session(max_retries=3, delay=2)
    def get(self, url, timeout=10):
        """Make a GET request with proper rate limiting and cookie refresh"""
        self._wait_for_rate_limit()
        
        if not self.cookies:
            self.get_cookies()
            
        response = self.session.get(url, cookies=self.cookies, timeout=timeout)
        
        # If unauthorized, try refreshing cookies once
        if response.status_code in [401, 403]:
            self.get_cookies()
            response = self.session.get(url, cookies=self.cookies, timeout=timeout)
            
        response.raise_for_status()
        return response
