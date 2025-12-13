"""
Kripto Portföy Risk Analiz Platformu
Ana Flask uygulaması
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_login import LoginManager, login_required, current_user
import os
import secrets
from dotenv import load_dotenv
from models import db, User
from auth import init_auth
from services.bybit_service import BybitService
from services.risk_analyzer import RiskAnalyzer
from services.portfolio_manager import PortfolioManager
from services.leverage_analyzer import LeverageAnalyzer
from services.position_sizer import PositionSizer
from services.bybit_private_api import BybitPrivateAPI

# Environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))

# Database configuration
database_url = os.getenv('DATABASE_URL')
if database_url:
    # Render PostgreSQL için
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Development için SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crypto_risk.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
CORS(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Lütfen giriş yapın'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize authentication
init_auth(app)

# Servisleri başlat
bybit_service = BybitService()
risk_analyzer = RiskAnalyzer(bybit_service)
portfolio_manager = PortfolioManager(bybit_service, risk_analyzer)
leverage_analyzer = LeverageAnalyzer(bybit_service, risk_analyzer)
position_sizer = PositionSizer(bybit_service, risk_analyzer)


@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')


@app.route('/api/prices', methods=['GET'])
def get_prices():
    """Popüler coinlerin fiyatlarını döndür"""
    try:
        symbols = request.args.get('symbols', 'BTC,ETH,BNB,SOL,ADA').split(',')
        prices = bybit_service.get_prices(symbols)
        return jsonify({'success': True, 'data': prices})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
@login_required
def analyze_portfolio():
    """Portföy analizi yap"""
    try:
        # Kullanım limiti kontrolü
        if not current_user.can_use_feature('portfolio_analysis'):
            return jsonify({
                'success': False,
                'error': 'Günlük analiz limitiniz doldu. Planınızı yükseltin veya yarın tekrar deneyin.'
            }), 403
        
        data = request.get_json()
        portfolio = data.get('portfolio', [])
        
        if not portfolio:
            return jsonify({'success': False, 'error': 'Portföy boş'}), 400
        
        # Analiz yap
        analysis = portfolio_manager.analyze_portfolio(portfolio)
        
        # Kullanım istatistiklerini artır
        try:
            current_user.increment_usage()
        except Exception as e:
            print(f"Kullanım istatistiği güncellenemedi: {e}")
        
        return jsonify({
            'success': True,
            'data': analysis,
            'usage': {
                'daily': current_user.daily_analyses,
                'total': current_user.total_analyses
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/suggest-rebalancing', methods=['POST'])
def suggest_rebalancing():
    """Rebalancing önerileri"""
    try:
        data = request.get_json()
        portfolio = data.get('portfolio', [])
        risk_profile = data.get('risk_profile', 'balanced')
        target_allocation = data.get('target_allocation', None)
        
        suggestions = portfolio_manager.suggest_rebalancing(
            portfolio, risk_profile, target_allocation
        )
        
        return jsonify({
            'success': True,
            'data': suggestions
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/market-data/<symbol>', methods=['GET'])
def get_market_data(symbol):
    """Bir coin için market verileri (24h değişim, hacim vb.)"""
    try:
        data = bybit_service.get_market_data(symbol)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/analyze-leverage', methods=['POST'])
@login_required
def analyze_leverage():
    """Kaldıraçlı pozisyonları analiz et"""
    try:
        # Kullanım limiti kontrolü
        if not current_user.can_use_feature('leverage_analysis'):
            return jsonify({
                'success': False,
                'error': 'Kaldıraç analizi limitiniz doldu. Planınızı yükseltin.'
            }), 403
        
        data = request.get_json()
        positions = data.get('positions', [])
        total_balance = float(data.get('total_balance', 0))
        
        if not positions:
            return jsonify({'success': False, 'error': 'Pozisyon listesi boş'}), 400
        
        analysis = leverage_analyzer.analyze_leverage_positions(positions, total_balance)
        
        # Kullanım istatistiklerini artır
        try:
            current_user.increment_usage()
        except Exception as e:
            print(f"Kullanım istatistiği güncellenemedi: {e}")
        
        return jsonify({
            'success': True,
            'data': analysis,
            'usage': {
                'daily': current_user.daily_analyses,
                'total': current_user.total_analyses
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/position-size', methods=['POST'])
@login_required
def calculate_position_size():
    """Optimal pozisyon boyutu hesapla"""
    try:
        # Kullanım limiti kontrolü
        if not current_user.can_use_feature('position_sizing'):
            return jsonify({
                'success': False,
                'error': 'Pozisyon boyutu hesaplama limitiniz doldu. Planınızı yükseltin.'
            }), 403
        
        data = request.get_json()
        symbol = data.get('symbol', '').upper()
        account_balance = float(data.get('account_balance', 0))
        risk_tolerance = data.get('risk_tolerance', 'moderate')
        leverage = int(data.get('leverage', 1))
        stop_loss_percentage = data.get('stop_loss_percentage', None)
        
        if not symbol or account_balance <= 0:
            return jsonify({'success': False, 'error': 'Geçersiz parametreler'}), 400
        
        result = position_sizer.calculate_optimal_position_size(
            symbol, account_balance, risk_tolerance, leverage, stop_loss_percentage
        )
        
        if 'error' in result:
            return jsonify({'success': False, 'error': result['error']}), 400
        
        # Kullanım istatistiklerini artır
        try:
            current_user.increment_usage()
        except Exception as e:
            print(f"Kullanım istatistiği güncellenemedi: {e}")
        
        return jsonify({
            'success': True,
            'data': result,
            'usage': {
                'daily': current_user.daily_analyses,
                'total': current_user.total_analyses
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stop-loss', methods=['POST'])
def recommend_stop_loss():
    """Stop-loss önerisi"""
    try:
        data = request.get_json()
        position = data.get('position', {})
        max_loss_percentage = float(data.get('max_loss_percentage', 2.0))
        
        if not position:
            return jsonify({'success': False, 'error': 'Pozisyon bilgisi eksik'}), 400
        
        recommendation = leverage_analyzer.recommend_stop_loss(position, max_loss_percentage)
        
        return jsonify({
            'success': True,
            'data': recommendation
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/risk-reward', methods=['POST'])
def calculate_risk_reward():
    """Risk/Reward oranı hesapla"""
    try:
        data = request.get_json()
        entry_price = float(data.get('entry_price', 0))
        stop_loss_price = float(data.get('stop_loss_price', 0))
        take_profit_price = float(data.get('take_profit_price', 0))
        side = data.get('side', 'Buy')
        
        if entry_price <= 0 or stop_loss_price <= 0 or take_profit_price <= 0:
            return jsonify({'success': False, 'error': 'Geçersiz fiyatlar'}), 400
        
        result = position_sizer.calculate_risk_reward_ratio(
            entry_price, stop_loss_price, take_profit_price, side
        )
        
        if 'error' in result:
            return jsonify({'success': False, 'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/portfolio-allocation', methods=['POST'])
def suggest_portfolio_allocation():
    """Portföy dağılım önerisi"""
    try:
        data = request.get_json()
        account_balance = float(data.get('account_balance', 0))
        risk_tolerance = data.get('risk_tolerance', 'moderate')
        number_of_positions = int(data.get('number_of_positions', 5))
        
        if account_balance <= 0:
            return jsonify({'success': False, 'error': 'Hesap bakiyesi geçersiz'}), 400
        
        result = position_sizer.suggest_portfolio_allocation(
            account_balance, risk_tolerance, number_of_positions
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Bybit API Entegrasyonu Route'ları
@app.route('/api/connect-bybit', methods=['POST'])
def connect_bybit():
    """Bybit API key'lerini bağla (session'da sakla)"""
    try:
        data = request.get_json()
        api_key = data.get('api_key', '').strip()
        api_secret = data.get('api_secret', '').strip()
        
        if not api_key or not api_secret:
            return jsonify({
                'success': False,
                'error': 'API Key ve Secret gereklidir'
            }), 400
        
        # API bağlantısını test et
        private_api = BybitPrivateAPI(api_key, api_secret)
        test_result = private_api.test_connection()
        
        if not test_result['success']:
            return jsonify({
                'success': False,
                'error': test_result['message'],
                'error_code': test_result.get('error_code'),
                'suggestion': test_result.get('suggestion', '')
            }), 400
        
        # Session'da sakla (güvenli - sadece bu oturum için)
        session['bybit_api_key'] = api_key
        session['bybit_api_secret'] = api_secret
        
        return jsonify({
            'success': True,
            'message': 'Bybit API bağlantısı başarılı!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/disconnect-bybit', methods=['POST'])
def disconnect_bybit():
    """Bybit API bağlantısını kes"""
    session.pop('bybit_api_key', None)
    session.pop('bybit_api_secret', None)
    
    return jsonify({
        'success': True,
        'message': 'Bybit bağlantısı kesildi'
    })


@app.route('/api/sync-positions', methods=['GET'])
def sync_positions():
    """Bybit'ten otomatik pozisyonları çek"""
    try:
        api_key = session.get('bybit_api_key')
        api_secret = session.get('bybit_api_secret')
        
        if not api_key or not api_secret:
            return jsonify({
                'success': False,
                'error': 'Bybit API bağlantısı yok. Lütfen önce bağlanın.'
            }), 400
        
        private_api = BybitPrivateAPI(api_key, api_secret)
        
        # Futures pozisyonları
        futures_positions = private_api.get_positions()
        
        # Spot pozisyonları
        spot_positions = private_api.get_spot_positions()
        
        # Wallet balance
        balances = private_api.get_wallet_balance()
        total_usdt = balances.get('USDT', {}).get('available', 0)
        
        return jsonify({
            'success': True,
            'data': {
                'futures_positions': futures_positions,
                'spot_positions': spot_positions,
                'balance': {
                    'usdt': total_usdt,
                    'all_balances': balances
                },
                'total_balance_usdt': total_usdt
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/bybit-status', methods=['GET'])
def bybit_status():
    """Bybit bağlantı durumunu kontrol et"""
    api_key = session.get('bybit_api_key')
    
    return jsonify({
        'connected': bool(api_key),
        'has_key': bool(api_key)
    })


# Database tablolarını oluştur
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tabloları başarıyla oluşturuldu/doğrulandı")
    except Exception as e:
        print(f"⚠️ Database tablo oluşturma hatası (devam ediliyor): {str(e)}")
        # Production'da database olmayabilir, uygulama çalışmaya devam eder

if __name__ == '__main__':
    # Production'da gunicorn kullanılır, bu sadece development için
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)

