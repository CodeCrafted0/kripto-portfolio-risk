"""
Kaldıraç (Leverage) Analiz Modülü
Kaldıraçlı işlemlerin risklerini analiz eder ve uyarılar verir
"""

from typing import List, Dict, Optional
import numpy as np
from services.bybit_service import BybitService
from services.risk_analyzer import RiskAnalyzer


class LeverageAnalyzer:
    """Kaldıraç analizi ve risk yönetimi"""
    
    def __init__(self, bybit_service: BybitService, risk_analyzer: RiskAnalyzer):
        self.bybit_service = bybit_service
        self.risk_analyzer = risk_analyzer
    
    def analyze_leverage_positions(self, positions: List[Dict], total_balance: float) -> Dict:
        """
        Kaldıraçlı pozisyonları analiz et
        
        positions: [
            {
                'symbol': 'BTC',
                'side': 'Buy' or 'Sell',
                'size': 10000,  # Pozisyon boyutu (USD)
                'leverage': 10,  # Kaldıraç oranı
                'entry_price': 45000,
                'current_price': 46000,
                'margin': 1000  # Kullanılan margin
            }
        ]
        """
        if not positions:
            return {
                'total_leverage_risk': 0,
                'warnings': [],
                'recommendations': [],
                'max_leverage_ratio': 0,
                'total_exposure': 0,
                'total_margin_used': 0,
                'margin_usage_percentage': 0,
                'positions_analysis': []
            }
        
        # GERÇEK ZAMANLI: Tüm coinlerin güncel fiyatlarını API'den çek
        symbols = [pos.get('symbol', '').upper() for pos in positions]
        current_prices = self.bybit_service.get_prices(symbols)
        
        warnings = []
        recommendations = []
        positions_analysis = []
        
        total_exposure = 0
        total_margin_used = 0
        total_pnl = 0
        max_leverage = 0
        
        for pos in positions:
            symbol = pos.get('symbol', '').upper()
            leverage = pos.get('leverage', 1)
            size = pos.get('size', 0)
            margin = pos.get('margin', size / leverage if leverage > 0 else size)
            entry_price = pos.get('entry_price', 0)
            side = pos.get('side', 'Buy')
            
            # GERÇEK ZAMANLI FİYAT: API'den güncel fiyatı al
            provided_price = pos.get('current_price')
            real_time_price = current_prices.get(symbol)
            
            # Öncelik: API'den gelen güncel fiyat > kullanıcı fiyatı > entry price
            if real_time_price and real_time_price > 0:
                current_price = real_time_price
            elif provided_price and provided_price > 0:
                current_price = provided_price
            else:
                current_price = entry_price
            
            # Pozisyona güncel fiyatı ekle
            pos['current_price'] = current_price
            
            # Pozisyon analizi (güncel fiyatla)
            pos_analysis = self._analyze_single_position(pos, total_balance)
            positions_analysis.append(pos_analysis)
            
            # Toplam PnL'e ekle
            total_pnl += pos_analysis.get('pnl_amount', 0)
            
            # Toplam exposure
            exposure = size if leverage > 0 else size
            total_exposure += exposure
            total_margin_used += margin
            
            # Maksimum kaldıraç
            max_leverage = max(max_leverage, leverage)
            
            # Risk uyarıları
            if leverage >= 10:
                warnings.append({
                    'type': 'HIGH_LEVERAGE',
                    'severity': 'CRITICAL',
                    'symbol': symbol,
                    'message': f'⚠️ {symbol} pozisyonunda {leverage}x kaldıraç KULLANILMIŞ! Bu çok riskli. Maksimum %{100/leverage} fiyat hareketiyle tüm margin kaybedilebilir.',
                    'leverage': leverage,
                    'recommendation': f'Kaldıracı en fazla 3-5x\'e düşürün veya pozisyonu azaltın.'
                })
            elif leverage >= 5:
                warnings.append({
                    'type': 'MODERATE_LEVERAGE',
                    'severity': 'WARNING',
                    'symbol': symbol,
                    'message': f'⚠️ {symbol} pozisyonunda {leverage}x kaldıraç kullanılıyor. Dikkatli olun.',
                    'leverage': leverage
                })
            
            # Liquidation risk
            liquidation_risk = self._calculate_liquidation_risk(pos, total_balance)
            if liquidation_risk['risk_percentage'] > 20:
                warnings.append({
                    'type': 'LIQUIDATION_RISK',
                    'severity': 'CRITICAL',
                    'symbol': symbol,
                    'message': f'🚨 {symbol} pozisyonu için liquidation riski %{liquidation_risk["risk_percentage"]:.1f}. Sadece %{liquidation_risk["price_drop_to_liquidate"]:.2f} fiyat değişimiyle tüm pozisyon kaybedilebilir!',
                    'price_drop_to_liquidate': liquidation_risk['price_drop_to_liquidate'],
                    'recommendation': 'Stop-loss koyun veya pozisyonu kapatın.'
                })
        
        # Toplam margin kullanımı
        margin_usage_percentage = (total_margin_used / total_balance * 100) if total_balance > 0 else 0
        
        if margin_usage_percentage > 80:
            warnings.append({
                'type': 'HIGH_MARGIN_USAGE',
                'severity': 'CRITICAL',
                'message': f'🚨 Margin kullanımınız %{margin_usage_percentage:.1f}! Çok yüksek. Yeni pozisyon açmayın.',
                'margin_usage': margin_usage_percentage,
                'recommendation': 'Bazı pozisyonları kapatarak margin serbest bırakın.'
            })
        elif margin_usage_percentage > 50:
            warnings.append({
                'type': 'MODERATE_MARGIN_USAGE',
                'severity': 'WARNING',
                'message': f'⚠️ Margin kullanımınız %{margin_usage_percentage:.1f}. Yeni pozisyon açarken dikkatli olun.',
                'margin_usage': margin_usage_percentage
            })
        
        # Genel öneriler
        if max_leverage > 5:
            recommendations.append({
                'type': 'REDUCE_LEVERAGE',
                'priority': 'HIGH',
                'message': f'Maksimum kaldıraç {max_leverage}x. Profesyonel yatırımcılar genelde 2-3x kullanır. Kaldıracı düşürün.'
            })
        
        # Toplam risk skoru
        total_leverage_risk = self._calculate_total_leverage_risk(
            positions, total_balance, margin_usage_percentage, max_leverage
        )
        
        from datetime import datetime
        
        return {
            'total_leverage_risk': round(total_leverage_risk, 2),
            'warnings': warnings,
            'recommendations': recommendations,
            'max_leverage_ratio': max_leverage,
            'total_exposure': round(total_exposure, 2),
            'total_margin_used': round(total_margin_used, 2),
            'margin_usage_percentage': round(margin_usage_percentage, 2),
            'positions_analysis': positions_analysis,
            'safe_margin_limit': round(total_balance * 0.3, 2),  # %30 güvenli limit
            'total_pnl': round(total_pnl, 2),  # Toplam kar/zarar
            'total_pnl_percentage': round((total_pnl / total_margin_used * 100) if total_margin_used > 0 else 0, 2),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Son güncelleme zamanı
        }
    
    def _analyze_single_position(self, position: Dict, total_balance: float) -> Dict:
        """Tek bir pozisyon için detaylı analiz"""
        symbol = position.get('symbol', '').upper()
        leverage = position.get('leverage', 1)
        size = position.get('size', 0)
        margin = position.get('margin', size / leverage if leverage > 0 else size)
        entry_price = position.get('entry_price', 0)
        current_price = position.get('current_price', entry_price)
        side = position.get('side', 'Buy')
        
        # PnL hesapla
        if entry_price > 0:
            price_change = ((current_price - entry_price) / entry_price) * 100
            if side == 'Sell':
                price_change = -price_change
            
            # Kaldıraçlı PnL
            pnl_percentage = price_change * leverage
            pnl_amount = margin * (pnl_percentage / 100)
        else:
            pnl_percentage = 0
            pnl_amount = 0
        
        # Liquidation fiyatı
        liquidation_price = self._calculate_liquidation_price(position)
        
        # Liquidation'a ne kadar uzak
        if liquidation_price and current_price > 0:
            if side == 'Buy':
                distance_to_liquidation = ((current_price - liquidation_price) / current_price) * 100
            else:
                distance_to_liquidation = ((liquidation_price - current_price) / current_price) * 100
        else:
            distance_to_liquidation = None
        
        # Risk skoru
        risk_score = min(leverage * 10, 100)  # 10x = 100 risk
        
        return {
            'symbol': symbol,
            'leverage': leverage,
            'size': round(size, 2),
            'margin': round(margin, 2),
            'pnl_percentage': round(pnl_percentage, 2),
            'pnl_amount': round(pnl_amount, 2),
            'liquidation_price': round(liquidation_price, 2) if liquidation_price else None,
            'distance_to_liquidation': round(distance_to_liquidation, 2) if distance_to_liquidation else None,
            'risk_score': round(risk_score, 2)
        }
    
    def _calculate_liquidation_price(self, position: Dict) -> Optional[float]:
        """Liquidation fiyatını hesapla"""
        leverage = position.get('leverage', 1)
        entry_price = position.get('entry_price', 0)
        side = position.get('side', 'Buy')
        margin_percentage = 100 / leverage  # %10 margin = 10x leverage
        
        if entry_price == 0 or leverage == 0:
            return None
        
        # Basitleştirilmiş hesaplama (gerçekte maintenance margin vb. faktörler var)
        # Liquidation genelde %90-95 margin kaybedildiğinde olur
        liquidation_threshold = 0.90  # %90 margin kaybedilince
        
        if side == 'Buy':
            # Long pozisyon için: Fiyat düşerse liquidation
            price_drop = (margin_percentage * liquidation_threshold) / 100
            liquidation_price = entry_price * (1 - price_drop)
        else:
            # Short pozisyon için: Fiyat yükselirse liquidation
            price_rise = (margin_percentage * liquidation_threshold) / 100
            liquidation_price = entry_price * (1 + price_rise)
        
        return liquidation_price
    
    def _calculate_liquidation_risk(self, position: Dict, total_balance: float) -> Dict:
        """Liquidation riskini hesapla"""
        current_price = position.get('current_price', position.get('entry_price', 0))
        liquidation_price = self._calculate_liquidation_price(position)
        side = position.get('side', 'Buy')
        
        if not liquidation_price or current_price == 0:
            return {
                'risk_percentage': 0,
                'price_drop_to_liquidate': 0
            }
        
        if side == 'Buy':
            price_drop_needed = ((current_price - liquidation_price) / current_price) * 100
        else:
            price_drop_needed = ((liquidation_price - current_price) / current_price) * 100
        
        # Risk yüzdesi: %10'dan az fiyat hareketiyle liquidation = yüksek risk
        if price_drop_needed < 5:
            risk_percentage = 90
        elif price_drop_needed < 10:
            risk_percentage = 70
        elif price_drop_needed < 20:
            risk_percentage = 50
        else:
            risk_percentage = 30
        
        return {
            'risk_percentage': risk_percentage,
            'price_drop_to_liquidate': abs(price_drop_needed)
        }
    
    def _calculate_total_leverage_risk(
        self, 
        positions: List[Dict], 
        total_balance: float,
        margin_usage: float,
        max_leverage: float
    ) -> float:
        """Toplam kaldıraç risk skoru (0-100)"""
        if not positions:
            return 0
        
        # Kaldıraç riski
        leverage_risk = min(max_leverage * 10, 100)
        
        # Margin kullanım riski
        margin_risk = min(margin_usage * 1.2, 100)  # %80 kullanım = 96 risk
        
        # Pozisyon sayısı riski (çok fazla pozisyon = yönetilemez)
        position_count_risk = min(len(positions) * 5, 50)
        
        # Ağırlıklı ortalama
        total_risk = (
            leverage_risk * 0.50 +  # %50 ağırlık
            margin_risk * 0.30 +    # %30 ağırlık
            position_count_risk * 0.20  # %20 ağırlık
        )
        
        return total_risk
    
    def recommend_position_size(
        self, 
        symbol: str, 
        account_balance: float, 
        risk_per_trade: float = 1.0,
        leverage: int = 1,
        stop_loss_percentage: float = 5.0
    ) -> Dict:
        """
        Optimal pozisyon boyutu önerisi
        
        risk_per_trade: İşlem başına risk (%1 = hesabın %1'i)
        stop_loss_percentage: Stop-loss mesafesi (%5 = %5 zarar durdur)
        """
        # Risk tutarı
        risk_amount = account_balance * (risk_per_trade / 100)
        
        # Stop-loss mesafesi ile pozisyon boyutu
        # Risk tutarı = (Pozisyon boyutu / kaldıraç) * (stop_loss / 100)
        # Pozisyon boyutu = (Risk tutarı * kaldıraç * 100) / stop_loss
        
        if stop_loss_percentage == 0:
            stop_loss_percentage = 1.0
        
        position_size = (risk_amount * leverage * 100) / stop_loss_percentage
        
        # Kaldıraçlı margin ihtiyacı
        margin_required = position_size / leverage if leverage > 0 else position_size
        
        # Güvenlik kontrolü: Margin hesabın %30'unu geçmemeli
        max_safe_margin = account_balance * 0.30
        if margin_required > max_safe_margin:
            position_size = max_safe_margin * leverage
            margin_required = max_safe_margin
        
        # Coin sayısı (fiyat gerekli)
        current_price = self.bybit_service.get_price(symbol)
        coin_amount = position_size / current_price if current_price and current_price > 0 else None
        
        return {
            'symbol': symbol,
            'recommended_position_size': round(position_size, 2),
            'margin_required': round(margin_required, 2),
            'coin_amount': round(coin_amount, 6) if coin_amount else None,
            'risk_amount': round(risk_amount, 2),
            'stop_loss_percentage': stop_loss_percentage,
            'leverage': leverage,
            'recommendation': f'{symbol} için önerilen pozisyon boyutu: ${position_size:,.2f} (${margin_required:,.2f} margin, {leverage}x kaldıraç). Maksimum ${risk_amount:,.2f} risk alınıyor.'
        }
    
    def recommend_stop_loss(self, position: Dict, max_loss_percentage: float = 2.0) -> Dict:
        """
        Stop-loss önerisi
        
        max_loss_percentage: Maksimum zarar yüzdesi (hesabın %2'si)
        """
        symbol = position.get('symbol', '').upper()
        entry_price = position.get('entry_price', 0)
        leverage = position.get('leverage', 1)
        side = position.get('side', 'Buy')
        margin = position.get('margin', 0)
        
        if entry_price == 0 or margin == 0:
            return {
                'stop_loss_price': None,
                'stop_loss_percentage': None,
                'recommendation': 'Girdi fiyatı veya margin bilgisi eksik.'
            }
        
        # Margin'in maksimum %2'si kadar zarar
        max_loss_amount = margin * (max_loss_percentage / 100)
        
        # Kaldıraçlı fiyat hareketi
        price_move_needed = (max_loss_amount / margin) * 100 / leverage
        
        if side == 'Buy':
            stop_loss_price = entry_price * (1 - price_move_needed / 100)
        else:
            stop_loss_price = entry_price * (1 + price_move_needed / 100)
        
        return {
            'symbol': symbol,
            'stop_loss_price': round(stop_loss_price, 2),
            'stop_loss_percentage': round(price_move_needed, 2),
            'max_loss_amount': round(max_loss_amount, 2),
            'recommendation': f'{symbol} için önerilen stop-loss: ${stop_loss_price:,.2f} (Girdi fiyatından %{price_move_needed:.2f} uzaklıkta). Maksimum zarar: ${max_loss_amount:,.2f}'
        }

