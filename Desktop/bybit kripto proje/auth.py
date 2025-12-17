"""
Authentication ve Authorization Modülü
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, User, SubscriptionPlan
from services.email_service import EmailService
from datetime import datetime, timedelta
import re
import threading

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()
_app = None  # Flask app instance'ını sakla


def init_auth(app):
    """Authentication'ı Flask app'e bağla"""
    global _app
    _app = app
    bcrypt.init_app(app)
    app.register_blueprint(auth_bp)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Kullanıcı kayıt"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        name = request.form.get('name', '').strip()
        
        # Validation
        if not email or not password:
            flash('Email ve şifre gereklidir', 'error')
            return render_template('auth/register.html')
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            flash('Geçerli bir email adresi girin', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 8:
            flash('Şifre en az 8 karakter olmalıdır', 'error')
            return render_template('auth/register.html')
        
        # Email zaten var mı?
        if User.query.filter_by(email=email).first():
            flash('Bu email adresi zaten kullanılıyor', 'error')
            return render_template('auth/register.html')
        
        # Yeni kullanıcı oluştur
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(
            email=email,
            password_hash=password_hash,
            name=name or None,
            subscription_plan=SubscriptionPlan.FREE,
            email_verified=False
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Email doğrulama kodu gönder (arka planda, timeout önlemek için)
        def send_email_async():
            try:
                with _app.app_context():
                    EmailService.send_verification_email(user)
            except Exception as e:
                print(f"Email gönderme hatası (arka plan): {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Thread başlat - email gönderimi arka planda yapılacak
        email_thread = threading.Thread(target=send_email_async)
        email_thread.daemon = True
        email_thread.start()
        
        # Hemen response döndür (timeout önlemek için)
        flash('Kayıt başarılı! Email adresinize 6 haneli doğrulama kodu gönderiliyor. Lütfen email\'inizi kontrol edin.', 'success')
        return redirect(url_for('auth.verify_email_code', email=user.email))
    
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Kullanıcı giriş"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Email ve şifre gereklidir', 'error')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Email veya şifre hatalı', 'error')
            return render_template('auth/login.html')
        
        # Şifre hash kontrolü
        if not user.password_hash:
            flash('Hesap hatası. Lütfen şifrenizi sıfırlayın.', 'error')
            return render_template('auth/login.html')
        
        # Şifre kontrolü - daha güvenli
        try:
            # password_hash string olmalı, eğer bytes ise decode et
            password_hash = user.password_hash
            if isinstance(password_hash, bytes):
                password_hash = password_hash.decode('utf-8')
            
            password_match = bcrypt.check_password_hash(password_hash, password)
            print(f"Login attempt - Email: {email}, Password match: {password_match}, Email verified: {user.email_verified}")
            
            if password_match:
                if not user.is_active:
                    flash('Hesabınız deaktif edilmiş', 'error')
                    return render_template('auth/login.html')
                
                # Email doğrulama ZORUNLU - doğrulanmamışsa giriş yapamaz
                if not user.email_verified:
                    flash('Email adresinizi doğrulamanız gerekiyor. Lütfen email adresinize gelen doğrulama kodunu girin.', 'warning')
                    return redirect(url_for('auth.verify_email_code', email=user.email))
                
                login_user(user, remember=True)  # Remember me özelliği
                user.last_login = datetime.utcnow()  # Son giriş zamanını güncelle
                db.session.commit()
                flash('Giriş başarılı! Hoş geldiniz!', 'success')
                
                # Yönlendirme
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                print(f"Password mismatch for email: {email}")
                flash('Email veya şifre hatalı', 'error')
        except Exception as e:
            # Hata loglama (production'da logger kullanılmalı)
            print(f"Login error: {str(e)}")
            import traceback
            traceback.print_exc()
            flash('Giriş hatası oluştu. Lütfen tekrar deneyin.', 'error')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Çıkış yap"""
    logout_user()
    flash('Çıkış yapıldı', 'info')
    return redirect(url_for('index'))


@auth_bp.route('/profile')
@login_required
def profile():
    """Kullanıcı profili"""
    return render_template('auth/profile.html', user=current_user)


@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    """Email doğrulama"""
    try:
        if not token:
            flash('Geçersiz doğrulama linki', 'error')
            return redirect(url_for('auth.login'))
        
        user, error = EmailService.verify_token(token)
        
        if error:
            flash(error, 'error')
            return redirect(url_for('auth.login'))
        
        if user:
            # Email doğrulandı, kullanıcıyı giriş yap
            login_user(user, remember=True)
            flash('Email adresiniz başarıyla doğrulandı! Artık giriş yapabilirsiniz.', 'success')
            return redirect(url_for('index'))
        
        flash('Geçersiz doğrulama linki', 'error')
        return redirect(url_for('auth.login'))
        
    except Exception as e:
        print(f"Email verification error: {str(e)}")
        flash('Email doğrulama sırasında bir hata oluştu. Lütfen tekrar deneyin.', 'error')
        return redirect(url_for('auth.login'))


@auth_bp.route('/email-verification-required')
def email_verification_required():
    """Email doğrulama gerektiği sayfası"""
    return render_template('auth/email_verification_required.html')


@auth_bp.route('/verify-email-code', methods=['GET', 'POST'])
def verify_email_code():
    """Email doğrulama kodu giriş sayfası"""
    email = request.args.get('email', '') or (request.form.get('email', '').strip().lower() if request.method == 'POST' else '')
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        code = request.form.get('code', '').strip()
        
        if not email or not code:
            flash('Email ve kod gereklidir', 'error')
            return render_template('auth/verify_email_code.html', email=email)
        
        user, error = EmailService.verify_code(email, code)
        
        if error:
            flash(error, 'error')
            return render_template('auth/verify_email_code.html', email=email)
        
        if user:
            # Email doğrulandı, kullanıcıyı giriş yap
            login_user(user, remember=True)
            flash('Email adresiniz başarıyla doğrulandı! Hoş geldiniz!', 'success')
            return redirect(url_for('index'))
    
    return render_template('auth/verify_email_code.html', email=email)


@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """Doğrulama kodunu tekrar gönder"""
    email = request.form.get('email', '').strip().lower()
    
    if not email:
        flash('Email adresi gereklidir', 'error')
        return redirect(url_for('auth.verify_email_code', email=email))
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        flash('Bu email adresi ile kayıtlı kullanıcı bulunamadı', 'error')
        return redirect(url_for('auth.verify_email_code', email=email))
    
    if user.email_verified:
        flash('Email adresiniz zaten doğrulanmış. Giriş yapabilirsiniz.', 'success')
        return redirect(url_for('auth.login'))
    
    # Email gönderimini arka planda yap (timeout önlemek için)
    def send_email_async():
        try:
            with _app.app_context():
                EmailService.send_verification_email(user)
        except Exception as e:
            print(f"Email gönderme hatası (arka plan): {str(e)}")
            import traceback
            traceback.print_exc()
    
    email_thread = threading.Thread(target=send_email_async)
    email_thread.daemon = True
    email_thread.start()
    
    flash('Doğrulama kodu gönderiliyor. Lütfen email adresinizi kontrol edin.', 'success')
    return redirect(url_for('auth.verify_email_code', email=email))


@auth_bp.route('/api/user-info')
@login_required
def user_info():
    """Kullanıcı bilgilerini JSON olarak döndür"""
    return jsonify({
        'success': True,
        'user': {
            'email': current_user.email,
            'name': current_user.name,
            'plan': current_user.subscription_plan.value,
            'email_verified': current_user.email_verified,
            'daily_analyses': current_user.daily_analyses,
            'total_analyses': current_user.total_analyses,
            'can_analyze': current_user.can_use_feature('portfolio_analysis')
        }
    })

