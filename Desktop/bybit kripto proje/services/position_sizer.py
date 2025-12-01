"""
Pozisyon Boyutu (Position Sizing) Hesaplama Modülü
Optimal pozisyon boyutlarını hesaplar ve risk yönetimi önerileri sunar
"""

from typing import Dict, Optional
from services.bybit_service import BybitService
from services.risk_analyzer import RiskAnalyzer


class PositionSizer:
    """Pozisyon boyutu hesaplama ve risk yönetimi"""
    
    def __init__(self, bybit_service: BybitService, risk_analyzer: RiskAnalyzer):
        self.bybit_service = bybit_service
        self.risk_analyzer = risk_analyzer
    
    def calculate_optimal_position_size(
        self,
        symbol: str,
        account_balance: float,
        risk_tolerance: str = 'moderate',
        leverage: int = 1,
        stop_loss_percentage: Optional[float] = None
    ) -> Dict:
        """
        Optimal pozisyon boyutu hesapla
        
        risk_tolerance: 'conservative', 'moderate', 'aggressive'
        """
        # Risk toleransına göre parametreler
        risk_params = {
            'conservative': {
                'risk_per_trade': 0.5,  # Hesabın %0.5'i
                'max_portfolio_risk': 2.0,  # Toplam portföy riski %2
                'default_stop_loss': 3.0,  # %3 stop-loss
                'max_leverage': 2
            },
            'moderate': {
                'risk_per_trade': 1.0,  # Hesabın %1'i
                'max_portfolio_risk': 5.0,
                'default_stop_loss': 5.0,
                'max_leverage': 3
            },
            'aggressive': {
                'risk_per_trade': 2.0,  # Hesabın %2'si
                'max_portfolio_risk': 10.0,
                'default_stop_loss': 7.0,
                'max_leverage': 5
            }
        }
        
        params = risk_params.get(risk_tolerance, risk_params['moderate'])
        
        # Leverage kontrolü
        if leverage > params['max_leverage']:
            return {
                'error': f'Risk toleransınıza göre maksimum kaldıraç {params["max_leverage"]}x olmalı. {leverage}x çok yüksek!',
                'recommended_leverage': params['max_leverage']
            }
        
        # Stop-loss belirle
        if stop_loss_percentage is None:
            stop_loss_percentage = params['default_stop_loss']
        
        # Volatiliteye göre stop-loss ayarla
        volatility = self.risk_analyzer._estimate_volatility(symbol) or 85
        if volatility > 100:
            stop_loss_percentage = max(stop_loss_percentage, 7.0)  # Yüksek volatilitede daha geniş stop
        
        # Risk tutarı
        risk_amount = account_balance * (params['risk_per_trade'] / 100)
        
        # Pozisyon boyutu hesapla
        # Risk = (Pozisyon / Leverage) * (StopLoss / 100)
        # Pozisyon = (Risk * Leverage * 100) / StopLoss
        position_size = (risk_amount * leverage * 100) / stop_loss_percentage
        
        # Margin ihtiyacı
        margin_required = position_size / leverage if leverage > 0 else position_size
        
        # Güvenlik limitleri
        max_position_per_coin = account_balance * 0.15  # Bir coin'e maksimum %15
        max_margin_usage = account_balance * 0.30  # Toplam margin kullanımı %30
        
        # Limitleri kontrol et
        if position_size > max_position_per_coin:
            position_size = max_position_per_coin
            margin_required = position_size / leverage if leverage > 0 else position_size
            risk_amount = (position_size / leverage) * (stop_loss_percentage / 100)
        
        if margin_required > max_margin_usage:
            margin_required = max_margin_usage
            position_size = margin_required * leverage
            risk_amount = margin_required * (stop_loss_percentage / 100)
        
        # Güncel fiyat al
        current_price = self.bybit_service.get_price(symbol)
        coin_amount = position_size / current_price if current_price and current_price > 0 else None
        
        # Öneri mesajları
        if leverage > 1:
            leverage_warning = f"⚠️ {leverage}x kaldıraç kullanılıyor. Dikkatli olun!"
        else:
            leverage_warning = ""
        
        coin_amount_str = f"{coin_amount:.6f}" if coin_amount else "N/A"
        stop_loss_price_str = f"${current_price * (1 - stop_loss_percentage/100):,.2f}" if current_price else "N/A"
        
        recommendation = (
            f"💡 {symbol} için önerilen pozisyon:\n"
            f"   • Pozisyon boyutu: ${position_size:,.2f}\n"
            f"   • Margin ihtiyacı: ${margin_required:,.2f}\n"
            f"   • Coin miktarı: {coin_amount_str}\n"
            f"   • Maksimum risk: ${risk_amount:,.2f} (%{params['risk_per_trade']})\n"
            f"   • Stop-loss: %{stop_loss_percentage} ({stop_loss_price_str})\n"
            f"{leverage_warning}"
        )
        
        return {
            'symbol': symbol,
            'position_size_usd': round(position_size, 2),
            'margin_required': round(margin_required, 2),
            'coin_amount': round(coin_amount, 6) if coin_amount else None,
            'risk_amount': round(risk_amount, 2),
            'risk_percentage': params['risk_per_trade'],
            'stop_loss_percentage': stop_loss_percentage,
            'stop_loss_price': round(current_price * (1 - stop_loss_percentage/100), 2) if current_price else None,
            'leverage': leverage,
            'current_price': round(current_price, 2) if current_price else None,
            'recommendation': recommendation,
            'warnings': [leverage_warning] if leverage > 1 else []
        }
    
    def calculate_risk_reward_ratio(
        self,
        entry_price: float,
        stop_loss_price: float,
        take_profit_price: float,
        side: str = 'Buy'
    ) -> Dict:
        """
        Risk/Reward oranını hesapla
        
        side: 'Buy' (Long) or 'Sell' (Short)
        """
        if entry_price == 0:
            return {'error': 'Girdi fiyatı 0 olamaz'}
        
        if side == 'Buy':
            risk = entry_price - stop_loss_price
            reward = take_profit_price - entry_price
        else:
            risk = stop_loss_price - entry_price
            reward = entry_price - take_profit_price
        
        if risk <= 0:
            return {'error': 'Stop-loss yanlış konumlandırılmış'}
        if reward <= 0:
            return {'error': 'Take-profit yanlış konumlandırılmış'}
        
        risk_reward_ratio = reward / risk
        
        # Değerlendirme
        if risk_reward_ratio >= 3:
            evaluation = 'Mükemmel - İşlem açılabilir'
        elif risk_reward_ratio >= 2:
            evaluation = 'İyi - Düşünülebilir'
        elif risk_reward_ratio >= 1.5:
            evaluation = 'Orta - Dikkatli olun'
        else:
            evaluation = 'Kötü - İşlem açmayın (Risk/Reward düşük)'
        
        return {
            'risk_reward_ratio': round(risk_reward_ratio, 2),
            'risk_percentage': round((risk / entry_price) * 100, 2),
            'reward_percentage': round((reward / entry_price) * 100, 2),
            'evaluation': evaluation,
            'recommendation': f'Risk/Reward: {risk_reward_ratio:.2f}:1. {evaluation}'
        }
    
    def suggest_portfolio_allocation(
        self,
        account_balance: float,
        risk_tolerance: str = 'moderate',
        number_of_positions: int = 5
    ) -> Dict:
        """
        Portföy için optimal pozisyon dağılımı öner
        
        Kaç pozisyon, her birine ne kadar
        """
        risk_params = {
            'conservative': {
                'max_total_exposure': 0.50,  # Maksimum %50 exposure
                'max_positions': 5,
                'risk_per_position': 0.5
            },
            'moderate': {
                'max_total_exposure': 0.70,
                'max_positions': 7,
                'risk_per_position': 1.0
            },
            'aggressive': {
                'max_total_exposure': 0.90,
                'max_positions': 10,
                'risk_per_position': 2.0
            }
        }
        
        params = risk_params.get(risk_tolerance, risk_params['moderate'])
        
        # Pozisyon sayısı kontrolü
        if number_of_positions > params['max_positions']:
            number_of_positions = params['max_positions']
        
        # Toplam kullanılabilir sermaye
        total_capital = account_balance * params['max_total_exposure']
        
        # Her pozisyon için sermaye (eşit dağıtım)
        capital_per_position = total_capital / number_of_positions
        
        # Her pozisyon için risk tutarı
        risk_per_position = account_balance * (params['risk_per_position'] / 100)
        
        return {
            'risk_tolerance': risk_tolerance,
            'number_of_positions': number_of_positions,
            'total_capital_usage': round(total_capital, 2),
            'capital_usage_percentage': round(params['max_total_exposure'] * 100, 1),
            'capital_per_position': round(capital_per_position, 2),
            'risk_per_position': round(risk_per_position, 2),
            'max_positions_recommended': params['max_positions'],
            'recommendation': (
                f"💼 {risk_tolerance.upper()} risk profili için öneriler:\n"
                f"   • Maksimum {number_of_positions} pozisyon açın\n"
                f"   • Her pozisyona ${capital_per_position:,.2f} ayırın\n"
                f"   • Toplam ${total_capital:,.2f} kullanın (Hesabın %{params['max_total_exposure']*100})\n"
                f"   • Her işlemde maksimum ${risk_per_position:,.2f} risk alın"
            )
        }

