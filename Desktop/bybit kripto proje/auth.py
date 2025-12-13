"""
Authentication ve Authorization Modülü
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, User, SubscriptionPlan
from services.email_service import EmailService
from datetime import datetime, timedelta
import re

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()


def init_auth(app):
    """Authentication'ı Flask app'e bağla"""
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
        
        # Email doğrulama email'i gönder
        try:
            EmailService.send_verification_email(user)
            flash('Kayıt başarılı! Lütfen email adresinize gelen doğrulama linkine tıklayın. Email\'inizi doğrulamadan giriş yapamazsınız.', 'success')
            # Email doğrulama ZORUNLU - giriş yapmadan email doğrulama sayfasına yönlendir
            return redirect(url_for('auth.email_verification_required'))
        except Exception as e:
            print(f"Email gönderme hatası: {e}")
            flash('Kayıt başarılı! Ancak doğrulama email\'i gönderilemedi. Lütfen daha sonra tekrar deneyin veya destek ekibimizle iletişime geçin.', 'warning')
            # Email gönderilemese bile kullanıcıya bilgi ver
            return redirect(url_for('auth.email_verification_required'))
    
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
            
            if bcrypt.check_password_hash(password_hash, password):
                if not user.is_active:
                    flash('Hesabınız deaktif edilmiş', 'error')
                    return render_template('auth/login.html')
                
                # Email doğrulama ZORUNLU - doğrulanmamışsa giriş yapamaz
                if not user.email_verified:
                    flash('Email adresinizi doğrulamanız gerekiyor. Lütfen email adresinize gelen doğrulama linkine tıklayın.', 'warning')
                    return redirect(url_for('auth.email_verification_required'))
                
                login_user(user, remember=True)  # Remember me özelliği
                user.last_login = datetime.utcnow()  # Son giriş zamanını güncelle
                db.session.commit()
                flash('Giriş başarılı! Hoş geldiniz!', 'success')
                
                # Yönlendirme
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                flash('Email veya şifre hatalı', 'error')
        except Exception as e:
            # Hata loglama (production'da logger kullanılmalı)
            print(f"Login error: {str(e)}")
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
    user, error = EmailService.verify_token(token)
    
    if error:
        flash(error, 'error')
        return redirect(url_for('auth.login'))
    
    if user:
        flash('Email adresiniz başarıyla doğrulandı!', 'success')
        login_user(user)
        return redirect(url_for('index'))
    
    flash('Geçersiz doğrulama linki', 'error')
    return redirect(url_for('auth.login'))


@auth_bp.route('/email-verification-required')
def email_verification_required():
    """Email doğrulama gerektiği sayfası"""
    return render_template('auth/email_verification_required.html')


@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """Doğrulama email'ini tekrar gönder"""
    email = request.form.get('email', '').strip().lower()
    
    if not email:
        flash('Email adresi gereklidir', 'error')
        return redirect(url_for('auth.email_verification_required'))
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        flash('Bu email adresi ile kayıtlı kullanıcı bulunamadı', 'error')
        return redirect(url_for('auth.email_verification_required'))
    
    if user.email_verified:
        flash('Email adresiniz zaten doğrulanmış. Giriş yapabilirsiniz.', 'success')
        return redirect(url_for('auth.login'))
    
    try:
        EmailService.send_verification_email(user)
        flash('Doğrulama email\'i tekrar gönderildi. Lütfen email adresinizi kontrol edin.', 'success')
    except Exception as e:
        flash('Email gönderilemedi. Lütfen daha sonra tekrar deneyin.', 'error')
    
    return redirect(url_for('auth.email_verification_required'))


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

