"""
Authentication ve Authorization Modülü
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, User, SubscriptionPlan
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
            subscription_plan=SubscriptionPlan.FREE
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Otomatik giriş yap
        login_user(user)
        flash('Kayıt başarılı! Hoş geldiniz!', 'success')
        return redirect(url_for('index'))
    
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Kullanıcı giriş"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Email ve şifre gereklidir', 'error')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            if not user.is_active:
                flash('Hesabınız deaktif edilmiş', 'error')
                return render_template('auth/login.html')
            
            login_user(user)
            flash('Giriş başarılı!', 'success')
            
            # Yönlendirme
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Email veya şifre hatalı', 'error')
    
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
            'daily_analyses': current_user.daily_analyses,
            'total_analyses': current_user.total_analyses,
            'can_analyze': current_user.can_use_feature('portfolio_analysis')
        }
    })

