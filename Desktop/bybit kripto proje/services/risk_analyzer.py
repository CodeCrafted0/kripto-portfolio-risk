"""
Risk Analiz Modülü - Portföy risk skorlarını hesaplar
"""

import numpy as np
from typing import List, Dict, Optional
from services.bybit_service import BybitService


class RiskAnalyzer:
    """Portföy risk analiz algoritmaları"""
    
    def __init__(self, bybit_service: BybitService):
        self.bybit_service = bybit_service
    
    def calculate_diversification_score(self, portfolio: List[Dict]) -> float:
        """
        Diversifikasyon skoru hesapla (0-100)
        Daha fazla coin ve dengeli dağılım = daha yüksek skor
        """
        if not portfolio:
            return 0
        
        total_value = sum(item.get('value', 0) for item in portfolio)
        if total_value == 0:
            return 0
        
        # Her coin'in portföy içindeki yüzdesi
        percentages = []
        for item in portfolio:
            value = item.get('value', 0)
            if value > 0:
                percentages.append(value / total_value)
        
        if not percentages:
            return 0
        
        # Herfindahl-Hirschman Index (HHI) - konsantrasyon ölçüsü
        # Düşük HHI = daha iyi diversifikasyon
        hhi = sum(p ** 2 for p in percentages)
        
        # Skoru normalize et (0-100)
        # HHI 0.2'den küçükse iyi diversifikasyon (5+ coin)
        # HHI 1.0 = tek coin (kötü)
        diversification_score = (1 - min(hhi, 1.0)) * 100
        
        # Coin sayısına göre bonus
        coin_count = len([p for p in percentages if p > 0.01])  # En az %1 olanlar
        coin_bonus = min(coin_count * 5, 20)  # En fazla 20 puan
        
        return min(diversification_score + coin_bonus, 100)
    
    def calculate_portfolio_volatility(self, portfolio: List[Dict]) -> Optional[float]:
        """
        Portföy toplam volatilitesi hesapla
        """
        if not portfolio:
            return None
        
        total_value = sum(item.get('value', 0) for item in portfolio)
        if total_value == 0:
            return None
        
        # Her coin için volatilite al ve ağırlıklı ortalama hesapla
        weighted_vol = 0
        valid_items = 0
        
        for item in portfolio:
            symbol = item.get('symbol', '').upper()
            value = item.get('value', 0)
            weight = value / total_value if total_value > 0 else 0
            
            if weight > 0:
                # Basit volatilite tahmini (gerçekte historical data gerekir)
                vol = self._estimate_volatility(symbol)
                if vol:
                    weighted_vol += vol * weight
                    valid_items += 1
        
        return weighted_vol if valid_items > 0 else None
    
    def _estimate_volatility(self, symbol: str) -> Optional[float]:
        """
        Coin için volatilite tahmini
        Gerçek uygulamada historical data kullanılmalı
        """
        # Popüler coinler için bilinen volatilite aralıkları
        volatility_map = {
            'BTC': 60,   # %60 yıllık volatilite
            'ETH': 80,
            'BNB': 70,
            'SOL': 100,
            'ADA': 90,
            'XRP': 85,
            'DOGE': 120,
            'MATIC': 95,
            'AVAX': 105,
            'LINK': 85,
        }
        
        return volatility_map.get(symbol, 85)  # Varsayılan: %85
    
    def calculate_correlation_risk(self, portfolio: List[Dict]) -> float:
        """
        Korelasyon riski - benzer coinler varsa risk artar
        """
        if len(portfolio) < 2:
            return 50  # Tek coin için orta risk
        
        # Basitleştirilmiş: Aynı kategoride coinler varsa risk artar
        # (Layer 1, DeFi, NFT vb.)
        
        symbols = [item.get('symbol', '').upper() for item in portfolio]
        
        # Layer 1 coinler (yüksek korelasyon)
        layer1 = {'BTC', 'ETH', 'BNB', 'SOL', 'ADA', 'AVAX', 'ATOM', 'DOT'}
        layer1_count = sum(1 for s in symbols if s in layer1)
        
        # Yüksek layer1 konsantrasyonu = yüksek korelasyon riski
        if layer1_count >= 3:
            return 70  # Yüksek korelasyon riski
        elif layer1_count >= 2:
            return 55
        else:
            return 40  # Düşük korelasyon riski
    
    def calculate_concentration_risk(self, portfolio: List[Dict]) -> float:
        """
        Konsantrasyon riski - tek coin'e çok yatırım varsa risk yüksek
        """
        if not portfolio:
            return 0
        
        total_value = sum(item.get('value', 0) for item in portfolio)
        if total_value == 0:
            return 0
        
        # En büyük pozisyonun yüzdesi
        max_value = max((item.get('value', 0) for item in portfolio), default=0)
        max_percentage = (max_value / total_value) * 100
        
        # En büyük 3 pozisyonun toplam yüzdesi
        values = sorted([item.get('value', 0) for item in portfolio], reverse=True)
        top3_percentage = (sum(values[:3]) / total_value) * 100
        
        # Risk skoru: tek coin %50+ ise yüksek risk
        if max_percentage >= 50:
            return 90
        elif max_percentage >= 30:
            return 70
        elif top3_percentage >= 80:
            return 60
        else:
            return 30
    
    def calculate_overall_risk_score(self, portfolio: List[Dict]) -> Dict:
        """
        Genel risk skoru hesapla (1-100)
        Yüksek skor = yüksek risk
        """
        if not portfolio:
            return {
                'overall_score': 50,
                'diversification_score': 0,
                'volatility_score': 50,
                'correlation_risk': 50,
                'concentration_risk': 50,
                'risk_level': 'ORTA'
            }
        
        # Alt skorları hesapla
        diversification = 100 - self.calculate_diversification_score(portfolio)
        volatility = self.calculate_portfolio_volatility(portfolio) or 50
        correlation = self.calculate_correlation_risk(portfolio)
        concentration = self.calculate_concentration_risk(portfolio)
        
        # Ağırlıklı ortalama
        overall_score = (
            diversification * 0.25 +  # %25 ağırlık
            min(volatility, 100) * 0.30 +  # %30 ağırlık
            correlation * 0.20 +  # %20 ağırlık
            concentration * 0.25  # %25 ağırlık
        )
        
        # Risk seviyesi belirle
        if overall_score >= 75:
            risk_level = 'ÇOK YÜKSEK'
        elif overall_score >= 60:
            risk_level = 'YÜKSEK'
        elif overall_score >= 40:
            risk_level = 'ORTA'
        elif overall_score >= 25:
            risk_level = 'DÜŞÜK'
        else:
            risk_level = 'ÇOK DÜŞÜK'
        
        return {
            'overall_score': round(overall_score, 2),
            'diversification_score': round(100 - diversification, 2),
            'volatility_score': round(min(volatility, 100), 2),
            'correlation_risk': round(correlation, 2),
            'concentration_risk': round(concentration, 2),
            'risk_level': risk_level
        }

