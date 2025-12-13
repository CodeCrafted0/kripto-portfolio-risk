"""
Email Service - Profesyonel email gönderme servisi
"""

from flask import url_for
from flask_mail import Message
from extensions import mail
import secrets
from datetime import datetime, timedelta
from models import db, User


class EmailService:
    """Email gönderme servisi"""
    
    @staticmethod
    def send_verification_email(user):
        """Email doğrulama linki gönder"""
        try:
            # Verification token oluştur
            token = secrets.token_urlsafe(32)
            user.email_verification_token = token
            user.email_verification_sent_at = datetime.utcnow()
            db.session.commit()
            
            # Verification URL oluştur
            verification_url = url_for('auth.verify_email', token=token, _external=True)
            
            # Email oluştur
            subject = "Email Adresinizi Doğrulayın - Kripto Portföy Risk Analiz"
            recipients = [user.email]
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; margin: 20px 0; font-weight: bold; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 0.9em; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Email Doğrulama</h1>
                    </div>
                    <div class="content">
                        <p>Merhaba {user.name or user.email},</p>
                        <p>Kripto Portföy Risk Analiz Platformu'na hoş geldiniz!</p>
                        <p>Hesabınızı aktifleştirmek için aşağıdaki butona tıklayın:</p>
                        <p style="text-align: center;">
                            <a href="{verification_url}" class="button">Email Adresimi Doğrula</a>
                        </p>
                        <p>Veya bu linki tarayıcınıza yapıştırın:</p>
                        <p style="word-break: break-all; color: #667eea;">{verification_url}</p>
                        <p><strong>Önemli:</strong> Bu link 24 saat geçerlidir.</p>
                        <p>Eğer bu işlemi siz yapmadıysanız, bu email'i görmezden gelebilirsiniz.</p>
                    </div>
                    <div class="footer">
                        <p>Kripto Portföy Risk Analiz Platformu<br>
                        Bu bir otomatik email'dir, lütfen cevap vermeyiniz.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_body = f"""
            Merhaba {user.name or user.email},
            
            Kripto Portföy Risk Analiz Platformu'na hoş geldiniz!
            
            Hesabınızı aktifleştirmek için aşağıdaki linke tıklayın:
            {verification_url}
            
            Bu link 24 saat geçerlidir.
            
            Eğer bu işlemi siz yapmadıysanız, bu email'i görmezden gelebilirsiniz.
            
            Kripto Portföy Risk Analiz Platformu
            """
            
            msg = Message(
                subject=subject,
                recipients=recipients,
                html=html_body,
                body=text_body
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Email gönderme hatası: {str(e)}")
            return False
    
    @staticmethod
    def verify_token(token):
        """Token doğrulama"""
        user = User.query.filter_by(email_verification_token=token).first()
        
        if not user:
            return None, "Geçersiz veya süresi dolmuş token"
        
        # Token süresi kontrolü (24 saat)
        if user.email_verification_sent_at:
            expires_at = user.email_verification_sent_at + timedelta(hours=24)
            if datetime.utcnow() > expires_at:
                return None, "Token süresi dolmuş. Lütfen yeni bir doğrulama email'i talep edin."
        
        # Email'i doğrula
        user.email_verified = True
        user.email_verification_token = None
        user.email_verification_sent_at = None
        db.session.commit()
        
        return user, None
