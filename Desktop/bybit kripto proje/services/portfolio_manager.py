"""
Portföy Yönetim Modülü - Portföy analizi ve rebalancing önerileri
"""

from typing import List, Dict, Optional
from services.bybit_service import BybitService
from services.risk_analyzer import RiskAnalyzer


class PortfolioManager:
    """Portföy yönetim ve analiz işlemleri"""
    
    def __init__(self, bybit_service: BybitService, risk_analyzer: RiskAnalyzer):
        self.bybit_service = bybit_service
        self.risk_analyzer = risk_analyzer
    
    def analyze_portfolio(self, portfolio: List[Dict]) -> Dict:
        """
        Portföyün tam analizini yap
        """
        # Güncel fiyatları al
        symbols = [item.get('symbol', '').upper() for item in portfolio]
        prices = self.bybit_service.get_prices(symbols)
        
        # Portföy değerlerini güncelle
        updated_portfolio = []
        total_value = 0
        
        for item in portfolio:
            symbol = item.get('symbol', '').upper()
            amount = float(item.get('amount', 0))
            current_price = prices.get(symbol, 0) or item.get('price', 0)
            
            value = amount * current_price
            total_value += value
            
            updated_portfolio.append({
                'symbol': symbol,
                'amount': amount,
                'price': current_price,
                'value': value,
                'percentage': 0  # Sonra hesaplanacak
            })
        
        # Yüzdeleri hesapla
        for item in updated_portfolio:
            if total_value > 0:
                item['percentage'] = (item['value'] / total_value) * 100
        
        # Risk analizi
        risk_analysis = self.risk_analyzer.calculate_overall_risk_score(updated_portfolio)
        
        # Her coin için volatilite
        coin_volatilities = {}
        for item in updated_portfolio:
            symbol = item['symbol']
            vol = self.risk_analyzer._estimate_volatility(symbol)
            if vol:
                coin_volatilities[symbol] = vol
        
        from datetime import datetime
        
        return {
            'portfolio': updated_portfolio,
            'total_value': round(total_value, 2),
            'risk_analysis': risk_analysis,
            'coin_count': len([p for p in updated_portfolio if p['value'] > 0]),
            'coin_volatilities': coin_volatilities,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Son güncelleme zamanı
        }
    
    def suggest_rebalancing(
        self, 
        portfolio: List[Dict], 
        risk_profile: str = 'balanced',
        target_allocation: Optional[Dict] = None
    ) -> Dict:
        """
        Rebalancing önerileri üret
        
        risk_profile: 'conservative', 'balanced', 'aggressive'
        """
        # Mevcut analiz
        current_analysis = self.analyze_portfolio(portfolio)
        current_portfolio = current_analysis['portfolio']
        total_value = current_analysis['total_value']
        
        # Hedef allocation belirle
        if target_allocation:
            target = target_allocation
        else:
            target = self._get_target_allocation(risk_profile, current_portfolio)
        
        # Önerileri hesapla
        suggestions = []
        
        for coin_target in target:
            symbol = coin_target['symbol']
            target_percentage = coin_target['percentage']
            
            # Mevcut pozisyonu bul
            current_item = next(
                (p for p in current_portfolio if p['symbol'] == symbol),
                None
            )
            
            current_percentage = current_item['percentage'] if current_item else 0
            current_value = current_item['value'] if current_item else 0
            target_value = total_value * (target_percentage / 100)
            
            difference = target_value - current_value
            difference_percentage = target_percentage - current_percentage
            
            if abs(difference_percentage) > 2:  # En az %2 fark varsa öner
                action = 'SAT' if difference < 0 else 'AL'
                suggestions.append({
                    'symbol': symbol,
                    'action': action,
                    'current_percentage': round(current_percentage, 2),
                    'target_percentage': round(target_percentage, 2),
                    'current_value': round(current_value, 2),
                    'target_value': round(target_value, 2),
                    'difference': round(abs(difference), 2),
                    'difference_percentage': round(abs(difference_percentage), 2)
                })
        
        return {
            'suggestions': suggestions,
            'risk_profile': risk_profile,
            'current_total': total_value
        }
    
    def _get_target_allocation(
        self, 
        risk_profile: str, 
        current_portfolio: List[Dict]
    ) -> List[Dict]:
        """
        Risk profiline göre hedef allocation
        """
        symbols = [item['symbol'] for item in current_portfolio]
        
        if risk_profile == 'conservative':
            # Konservatif: BTC ve ETH ağırlıklı
            return [
                {'symbol': 'BTC', 'percentage': 60},
                {'symbol': 'ETH', 'percentage': 30},
                {'symbol': 'STABLE', 'percentage': 10}  # Stablecoin
            ]
        elif risk_profile == 'aggressive':
            # Agresif: Daha fazla altcoin
            allocations = [
                {'symbol': 'BTC', 'percentage': 30},
                {'symbol': 'ETH', 'percentage': 25}
            ]
            
            # Kalan %45'i diğer coinlere dağıt
            other_coins = [s for s in symbols if s not in ['BTC', 'ETH']]
            if other_coins:
                per_coin = 45 / len(other_coins)
                for coin in other_coins:
                    allocations.append({'symbol': coin, 'percentage': min(per_coin, 15)})
            
            return allocations
        else:  # balanced
            # Dengeli: BTC, ETH, ve diğerleri dengeli
            allocations = [
                {'symbol': 'BTC', 'percentage': 40},
                {'symbol': 'ETH', 'percentage': 30}
            ]
            
            # Kalan %30'u diğer coinlere dağıt
            other_coins = [s for s in symbols if s not in ['BTC', 'ETH']]
            if other_coins:
                per_coin = 30 / len(other_coins)
                for coin in other_coins:
                    allocations.append({'symbol': coin, 'percentage': min(per_coin, 15)})
            
            return allocations

