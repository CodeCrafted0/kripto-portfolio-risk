"""
Email Service - Profesyonel email gönderme servisi
"""

from flask import url_for, current_app
from flask_mail import Message
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
            
            # Email ayarlarını kontrol et
            mail_server = current_app.config.get('MAIL_SERVER')
            mail_username = current_app.config.get('MAIL_USERNAME')
            mail_password = current_app.config.get('MAIL_PASSWORD')
            
            if not mail_server or not mail_username or not mail_password:
                print(f"Email gönderme hatası: Gerekli email ayarları eksik!")
                print(f"MAIL_SERVER: {mail_server}")
                print(f"MAIL_USERNAME: {mail_username}")
                print(f"MAIL_PASSWORD ayarlı mı: {bool(mail_password)}")
                return False
            
            # Mail extension'ını app context'ten al
            from extensions import mail
            
            msg = Message(
                subject=subject,
                recipients=recipients,
                html=html_body,
                body=text_body,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER', mail_username)
            )
            
            # Email göndermeyi dene
            mail.send(msg)
            print(f"Email başarıyla gönderildi: {user.email}")
            return True
            
        except Exception as e:
            error_msg = str(e)
            print(f"Email gönderme hatası: {error_msg}")
            import traceback
            traceback.print_exc()
            
            # Özel hata mesajları
            if "authentication failed" in error_msg.lower() or "535" in error_msg:
                print("HATA: Email authentication başarısız! MAIL_USERNAME ve MAIL_PASSWORD kontrol edin.")
            elif "connection" in error_msg.lower() or "refused" in error_msg.lower():
                print("HATA: SMTP server'a bağlanılamıyor! MAIL_SERVER ve MAIL_PORT kontrol edin.")
            elif "timeout" in error_msg.lower():
                print("HATA: Email gönderimi zaman aşımına uğradı!")
            
            return False
    
    @staticmethod
    def verify_token(token):
        """Token doğrulama"""
        try:
            if not token:
                return None, "Geçersiz doğrulama linki"
            
            user = User.query.filter_by(email_verification_token=token).first()
            
            if not user:
                return None, "Geçersiz veya süresi dolmuş token. Lütfen yeni bir doğrulama email'i talep edin."
            
            # Zaten doğrulanmış mı?
            if user.email_verified:
                return user, None  # Kullanıcı zaten doğrulanmış, hata yok
            
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
            
        except Exception as e:
            print(f"Token verification error: {str(e)}")
            db.session.rollback()
            return None, "Email doğrulama sırasında bir hata oluştu. Lütfen tekrar deneyin."
