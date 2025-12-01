"""
Bybit Private API Servisi - Kullanıcının API key'leri ile pozisyonlarını çeker
"""

import requests
import hmac
import hashlib
import time
from typing import List, Dict, Optional
from urllib.parse import urlencode


class BybitPrivateAPI:
    """Bybit Private API ile kullanıcı pozisyonlarını çeker"""
    
    BASE_URL = "https://api.bybit.com"
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
    
    def _generate_signature(self, params: Dict) -> tuple:
        """API signature oluştur - Bybit API v5 için"""
        if not self.api_secret:
            return "", "", ""
        
        # Timestamp ve recvWindow ekle
        timestamp = str(int(time.time() * 1000))
        recv_window = "5000"
        
        # Parametrelere ekle (kopyasını al, orijinalini değiştirme)
        sig_params = params.copy()
        sig_params['api_key'] = self.api_key
        sig_params['timestamp'] = timestamp
        sig_params['recvWindow'] = recv_window
        
        # Sıralı string oluştur (Bybit API v5 format)
        param_str = urlencode(sorted(sig_params.items()))
        
        # HMAC SHA256 signature
        signature = hmac.new(
            bytes(self.api_secret, 'utf-8'),
            bytes(param_str, 'utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature, timestamp, recv_window
    
    def _make_request(self, endpoint: str, params: Dict = None, return_full_response: bool = False) -> Optional[Dict]:
        """Private API isteği yap - Bybit API v5"""
        if not self.api_key or not self.api_secret:
            return None
        
        if params is None:
            params = {}
        
        # Signature oluştur ve parametrelere ekle
        signature, timestamp, recv_window = self._generate_signature(params.copy())
        
        # Final parametreler
        final_params = {
            'api_key': self.api_key,
            'timestamp': timestamp,
            'recvWindow': recv_window,
            'sign': signature,
            **params
        }
        
        try:
            url = f"{self.BASE_URL}{endpoint}"
            response = self.session.get(url, params=final_params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if return_full_response:
                return data
            
            if data.get('retCode') == 0:
                return data.get('result', {})
            else:
                error_msg = data.get('retMsg', 'Bilinmeyen hata')
                error_code = data.get('retCode', 'N/A')
                print(f"Bybit API Hatası [{error_code}]: {error_msg}")
                return {'error': error_msg, 'code': error_code}
        except requests.exceptions.RequestException as e:
            print(f"API isteği hatası: {e}")
            return {'error': f'Bağlantı hatası: {str(e)}'}
        except Exception as e:
            print(f"Beklenmeyen hata: {e}")
            return {'error': f'Beklenmeyen hata: {str(e)}'}
    
    def get_wallet_balance(self, coin: str = None) -> Dict:
        """
        Cüzdan bakiyesini çek
        
        coin: Belirli bir coin için (örn: 'USDT') veya None (tüm coinler)
        """
        params = {'accountType': 'UNIFIED'}  # Unified account
        
        result = self._make_request('/v5/account/wallet-balance', params)
        
        if not result:
            return {}
        
        # Bakiye bilgilerini parse et
        balances = {}
        coin_list = result.get('list', [])
        
        for account in coin_list:
            coins = account.get('coin', [])
            for coin_data in coins:
                coin_symbol = coin_data.get('coin', '')
                available = float(coin_data.get('availableToWithdraw', 0))
                total = float(coin_data.get('walletBalance', 0))
                
                if coin and coin_symbol != coin:
                    continue
                
                if available > 0 or total > 0:
                    balances[coin_symbol] = {
                        'available': available,
                        'total': total,
                        'locked': total - available
                    }
        
        return balances
    
    def get_positions(self, symbol: str = None) -> List[Dict]:
        """
        Açık pozisyonları çek
        
        symbol: Belirli bir coin için (örn: 'BTCUSDT') veya None (tüm pozisyonlar)
        """
        params = {
            'category': 'linear',  # Linear futures
            'settleCoin': 'USDT'
        }
        
        if symbol:
            params['symbol'] = symbol
        
        result = self._make_request('/v5/position/list', params)
        
        if not result:
            return []
        
        positions = []
        position_list = result.get('list', [])
        
        for pos in position_list:
            size = float(pos.get('size', 0))
            
            # Sadece açık pozisyonları al (size > 0)
            if size > 0:
                symbol_name = pos.get('symbol', '')
                side = pos.get('side', '')  # 'Buy' veya 'Sell'
                leverage = float(pos.get('leverage', 1))
                entry_price = float(pos.get('avgPrice', 0))
                mark_price = float(pos.get('markPrice', 0))
                unrealized_pnl = float(pos.get('unrealisedPnl', 0))
                
                # Pozisyon boyutu (USD)
                position_value = size * mark_price
                
                # Margin (hesaplamalı)
                margin = position_value / leverage if leverage > 0 else position_value
                
                positions.append({
                    'symbol': symbol_name.replace('USDT', ''),
                    'side': side,
                    'size': position_value,
                    'leverage': leverage,
                    'entry_price': entry_price,
                    'current_price': mark_price,
                    'margin': margin,
                    'unrealized_pnl': unrealized_pnl,
                    'quantity': size
                })
        
        return positions
    
    def get_spot_positions(self) -> List[Dict]:
        """Spot pozisyonları çek (coin miktarları)"""
        balances = self.get_wallet_balance()
        positions = []
        
        for coin, balance_data in balances.items():
            if coin == 'USDT':  # USDT'yi hariç tut
                continue
            
            total = balance_data['total']
            if total > 0:
                positions.append({
                    'symbol': coin,
                    'amount': total,
                    'available': balance_data['available']
                })
        
        return positions
    
    def test_connection(self) -> Dict:
        """API bağlantısını test et - detaylı hata mesajları ile"""
        try:
            params = {'accountType': 'UNIFIED'}
            result = self._make_request('/v5/account/wallet-balance', params, return_full_response=True)
            
            if result is None:
                return {
                    'success': False,
                    'message': 'API yanıtı alınamadı. API key ve secret\'ı kontrol edin.',
                    'error_code': 'NO_RESPONSE'
                }
            
            ret_code = result.get('retCode', -1)
            ret_msg = result.get('retMsg', 'Bilinmeyen hata')
            
            if ret_code == 0:
                return {
                    'success': True,
                    'message': '✅ API bağlantısı başarılı!',
                    'account_type': 'UNIFIED'
                }
            elif ret_code == 10003:
                return {
                    'success': False,
                    'message': '❌ Geçersiz API Key. API Key\'inizi kontrol edin.',
                    'error_code': ret_code,
                    'suggestion': 'Bybit API Management sayfasında API Key\'inizin aktif olduğunu kontrol edin.'
                }
            elif ret_code == 10004:
                return {
                    'success': False,
                    'message': '❌ Yanlış signature. API Secret\'ınızı kontrol edin.',
                    'error_code': ret_code,
                    'suggestion': 'API Secret\'ınızın doğru kopyalandığından emin olun (boşluk vs. olmamalı).'
                }
            elif ret_code == 10006:
                return {
                    'success': False,
                    'message': '❌ IP adresi kısıtlaması! IP adresiniz whitelist\'te değil.',
                    'error_code': ret_code,
                    'suggestion': 'Bybit API Management\'ta IP kısıtlaması varsa, kendi IP\'nizi ekleyin veya kısıtlamayı kaldırın.'
                }
            elif ret_code == 33004:
                return {
                    'success': False,
                    'message': '❌ API Key izinleri yetersiz. "Read" izni gerekli.',
                    'error_code': ret_code,
                    'suggestion': 'Bybit\'te API Key izinlerinizi kontrol edin: Unified Trading > Contract > Positions, SPOT > Trade, Assets > Wallet > Account Transfer'
                }
            else:
                return {
                    'success': False,
                    'message': f'❌ API Hatası [{ret_code}]: {ret_msg}',
                    'error_code': ret_code,
                    'error_message': ret_msg
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'❌ Bağlantı hatası: {str(e)}',
                'error_code': 'EXCEPTION'
            }

