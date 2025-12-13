"""
Database Models - Kullanıcı ve Abonelik Yönetimi
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import enum

db = SQLAlchemy()


class SubscriptionPlan(enum.Enum):
    """Abonelik planları"""
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"


class User(UserMixin, db.Model):
    """Kullanıcı modeli"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Abonelik bilgileri
    subscription_plan = db.Column(db.Enum(SubscriptionPlan), default=SubscriptionPlan.FREE)
    subscription_started = db.Column(db.DateTime, nullable=True)
    subscription_ends = db.Column(db.DateTime, nullable=True)
    stripe_customer_id = db.Column(db.String(255), nullable=True)
    stripe_subscription_id = db.Column(db.String(255), nullable=True)
    
    # Kullanım istatistikleri
    total_analyses = db.Column(db.Integer, default=0)
    daily_analyses = db.Column(db.Integer, default=0)
    last_analysis_date = db.Column(db.Date, nullable=True)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def can_use_feature(self, feature_name: str) -> bool:
        """Kullanıcının bir özelliği kullanıp kullanamayacağını kontrol et"""
        if self.subscription_plan == SubscriptionPlan.PRO:
            return True
        elif self.subscription_plan == SubscriptionPlan.STARTER:
            # Starter plan özellikleri
            allowed_features = ['portfolio_analysis', 'leverage_analysis', 'position_sizing']
            return feature_name in allowed_features
        else:  # FREE
            # Free plan limitleri
            if feature_name == 'portfolio_analysis':
                return self.daily_analyses < 10  # Günde 10 analiz
            return False
    
    def reset_daily_usage(self):
        """Günlük kullanımı sıfırla (her gün çalıştırılmalı)"""
        today = datetime.utcnow().date()
        if self.last_analysis_date != today:
            self.daily_analyses = 0
            self.last_analysis_date = today
            db.session.commit()
    
    def increment_usage(self):
        """Kullanım sayacını artır"""
        self.reset_daily_usage()
        self.daily_analyses += 1
        self.total_analyses += 1
        db.session.commit()


class UsageLog(db.Model):
    """Kullanım logları - Analytics için"""
    __tablename__ = 'usage_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    feature_name = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    metadata = db.Column(db.JSON, nullable=True)  # Ek bilgiler (coin sayısı, vs.)
    
    user = db.relationship('User', backref=db.backref('usage_logs', lazy=True))
    
    def __repr__(self):
        return f'<UsageLog {self.user_id} - {self.feature_name}>'

