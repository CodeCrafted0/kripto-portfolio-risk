"""
Bybit API servisi - Kripto fiyat verilerini çeker
"""

import requests
import time
from typing import List, Dict, Optional


class BybitService:
    """Bybit API ile etkileşim"""
    
    BASE_URL = "https://api.bybit.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.cache = {}
        self.cache_time = 60  # 60 saniye cache
    
    def get_price(self, symbol: str) -> Optional[float]:
        """Tek bir coin için fiyat al"""
        try:
            # Bybit format: BTCUSDT
            if not symbol.endswith('USDT'):
                symbol = f"{symbol}USDT"
            
            url = f"{self.BASE_URL}/v5/market/tickers"
            params = {'category': 'spot', 'symbol': symbol}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('retCode') == 0 and data.get('result', {}).get('list'):
                ticker = data['result']['list'][0]
                return float(ticker.get('lastPrice', 0))
            
            return None
        except Exception as e:
            print(f"Hata {symbol} fiyatı alınırken: {e}")
            return None
    
    def get_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Birden fazla coin için fiyat al"""
        prices = {}
        
        # Bybit'te tek sorguda tüm tickerları alabiliriz
        try:
            url = f"{self.BASE_URL}/v5/market/tickers"
            params = {'category': 'spot'}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('retCode') == 0:
                tickers = data.get('result', {}).get('list', [])
                
                for symbol in symbols:
                    # Symbol formatını düzelt
                    search_symbol = symbol
                    if not search_symbol.endswith('USDT'):
                        search_symbol = f"{symbol}USDT"
                    
                    # Ticker listesinde ara
                    for ticker in tickers:
                        if ticker.get('symbol') == search_symbol:
                            prices[symbol] = float(ticker.get('lastPrice', 0))
                            break
                    else:
                        # Bulunamadıysa None ekle
                        prices[symbol] = None
        except Exception as e:
            print(f"Hata fiyatlar alınırken: {e}")
            # Fallback: tek tek al
            for symbol in symbols:
                prices[symbol] = self.get_price(symbol)
        
        return prices
    
    def get_market_data(self, symbol: str) -> Dict:
        """Bir coin için detaylı market verileri"""
        try:
            if not symbol.endswith('USDT'):
                symbol = f"{symbol}USDT"
            
            url = f"{self.BASE_URL}/v5/market/tickers"
            params = {'category': 'spot', 'symbol': symbol}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('retCode') == 0 and data.get('result', {}).get('list'):
                ticker = data['result']['list'][0]
                
                return {
                    'symbol': symbol.replace('USDT', ''),
                    'price': float(ticker.get('lastPrice', 0)),
                    'change24h': float(ticker.get('price24hPcnt', 0)) * 100,
                    'high24h': float(ticker.get('highPrice24h', 0)),
                    'low24h': float(ticker.get('lowPrice24h', 0)),
                    'volume24h': float(ticker.get('volume24h', 0)),
                    'turnover24h': float(ticker.get('turnover24h', 0))
                }
            
            return {}
        except Exception as e:
            print(f"Hata market data alınırken: {e}")
            return {}
    
    def get_historical_volatility(self, symbol: str, days: int = 30) -> Optional[float]:
        """Tarihsel volatilite hesapla"""
        try:
            if not symbol.endswith('USDT'):
                symbol = f"{symbol}USDT"
            
            # Kline (candlestick) verilerini al
            url = f"{self.BASE_URL}/v5/market/kline"
            params = {
                'category': 'spot',
                'symbol': symbol,
                'interval': 'D',  # Günlük
                'limit': days
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('retCode') == 0:
                klines = data.get('result', {}).get('list', [])
                if len(klines) < 2:
                    return None
                
                # Fiyat değişimlerini hesapla
                returns = []
                for i in range(1, len(klines)):
                    prev_close = float(klines[i-1][4])  # Kapanış fiyatı
                    curr_close = float(klines[i][4])
                    if prev_close > 0:
                        returns.append((curr_close - prev_close) / prev_close)
                
                if returns:
                    import numpy as np
                    # Volatilite = standart sapma
                    volatility = np.std(returns) * np.sqrt(365) * 100  # Yıllık yüzde
                    return volatility
            
            return None
        except Exception as e:
            print(f"Hata volatilite hesaplanırken: {e}")
            return None

