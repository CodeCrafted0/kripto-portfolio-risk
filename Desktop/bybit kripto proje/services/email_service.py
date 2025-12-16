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
        """Email doğrulama kodu gönder (6 haneli)"""
        try:
            # 6 haneli kod oluştur
            import random
            code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            user.email_verification_code = code
            user.email_verification_sent_at = datetime.utcnow()
            db.session.commit()
            
            print(f"Email doğrulama kodu oluşturuldu: {code} (Email: {user.email})")
            
            # Email oluştur
            subject = "Email Doğrulama Kodu - Kripto Portföy Risk Analiz"
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
                    .code-box {{ background: white; border: 3px solid #667eea; border-radius: 10px; padding: 20px; text-align: center; margin: 30px 0; }}
                    .code {{ font-size: 36px; font-weight: bold; letter-spacing: 10px; color: #667eea; font-family: 'Courier New', monospace; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 0.9em; }}
                    .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Email Doğrulama Kodu</h1>
                    </div>
                    <div class="content">
                        <p>Merhaba {user.name or user.email},</p>
                        <p>Kripto Portföy Risk Analiz Platformu'na hoş geldiniz!</p>
                        <p>Hesabınızı aktifleştirmek için aşağıdaki doğrulama kodunu kullanın:</p>
                        <div class="code-box">
                            <div class="code">{code}</div>
                        </div>
                        <p style="text-align: center;">Bu kodu doğrulama sayfasına girin.</p>
                        <div class="warning">
                            <strong>⚠️ Önemli:</strong> Bu kod 10 dakika geçerlidir ve sadece bir kez kullanılabilir.
                        </div>
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
            
            Hesabınızı aktifleştirmek için aşağıdaki doğrulama kodunu kullanın:
            
            {code}
            
            Bu kodu doğrulama sayfasına girin.
            
            ÖNEMLİ: Bu kod 10 dakika geçerlidir ve sadece bir kez kullanılabilir.
            
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
    def verify_code(email, code):
        """6 haneli kod ile email doğrulama"""
        try:
            if not email or not code:
                return None, "Email ve kod gereklidir"
            
            # Kod'u temizle (boşlukları kaldır)
            code = code.strip().replace(' ', '').replace('-', '')
            
            if len(code) != 6 or not code.isdigit():
                return None, "Geçersiz kod formatı. 6 haneli sayısal kod giriniz."
            
            user = User.query.filter_by(email=email.lower()).first()
            
            if not user:
                return None, "Kullanıcı bulunamadı"
            
            # Zaten doğrulanmış mı?
            if user.email_verified:
                return user, None  # Kullanıcı zaten doğrulanmış, hata yok
            
            # Kod kontrolü
            if not user.email_verification_code:
                return None, "Doğrulama kodu bulunamadı. Lütfen yeni bir kod talep edin."
            
            if user.email_verification_code != code:
                return None, "Geçersiz doğrulama kodu. Lütfen tekrar deneyin."
            
            # Kod süresi kontrolü (10 dakika)
            if user.email_verification_sent_at:
                expires_at = user.email_verification_sent_at + timedelta(minutes=10)
                if datetime.utcnow() > expires_at:
                    return None, "Kod süresi dolmuş. Lütfen yeni bir doğrulama kodu talep edin."
            
            # Email'i doğrula
            user.email_verified = True
            user.email_verification_code = None
            user.email_verification_token = None
            user.email_verification_sent_at = None
            db.session.commit()
            
            print(f"Email doğrulandı: {user.email}")
            return user, None
            
        except Exception as e:
            print(f"Code verification error: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return None, "Email doğrulama sırasında bir hata oluştu. Lütfen tekrar deneyin."
