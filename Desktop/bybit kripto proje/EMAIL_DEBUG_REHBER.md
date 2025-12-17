# 📧 Email Gönderme Sorunu - Debug Rehberi

## ❌ Sorun: Email'e Kod Gelmiyor

### Adım 1: Render Loglarını Kontrol Edin

1. Render Dashboard → **kripto-portfolio-risk** servisi
2. **Logs** sekmesine gidin
3. Şu mesajları arayın:
   - ✅ `Email başarıyla gönderildi: ...` → Email gönderildi
   - ❌ `Email gönderme hatası: ...` → Hata var
   - ❌ `Gerekli email ayarları eksik!` → Environment variables eksik

### Adım 2: Environment Variables Kontrolü

Render Dashboard → **Settings** → **Environment Variables**

Şu değişkenlerin **TAMAMININ** olması gerekiyor:

1. **MAIL_SERVER** = `smtp.gmail.com`
2. **MAIL_PORT** = `587`
3. **MAIL_USE_TLS** = `True`
4. **MAIL_USERNAME** = `your-email@gmail.com` (SİZİN GMAIL ADRESİNİZ)
5. **MAIL_PASSWORD** = (Gmail App Password - 16 karakter) ⚠️ **EN ÖNEMLİSİ**
6. **MAIL_DEFAULT_SENDER** = `your-email@gmail.com` (veya `noreply@kriptorisk.com`)

### Adım 3: Gmail App Password Kontrolü

**Gmail App Password doğru mu?**

1. https://myaccount.google.com/apppasswords
2. **"Mail"** app password'unuzun olduğundan emin olun
3. Eğer yoksa:
   - **2-Step Verification** açık olmalı
   - **App passwords** → **Mail** → **Generate**
   - 16 karakterlik şifreyi kopyalayın (boşluklar olmadan)
   - Render'da `MAIL_PASSWORD` olarak ekleyin

### Adım 4: Test Email Gönderme

Render loglarında şu mesajları görüyor musunuz?

```
Email doğrulama kodu oluşturuldu: 123456 (Email: user@email.com)
Email başarıyla gönderildi: user@email.com, Kod: 123456
```

**Eğer "Email başarıyla gönderildi" görüyorsanız ama email gelmiyorsa:**

1. **Spam klasörünü** kontrol edin
2. **Gmail** → **All Mail** klasörüne bakın
3. Email filtresi olabilir mi?

**Eğer hata görüyorsanız:**

- `authentication failed` → MAIL_USERNAME veya MAIL_PASSWORD yanlış
- `connection refused` → MAIL_SERVER veya MAIL_PORT yanlış
- `timeout` → Network sorunu (geçici olabilir)

### Adım 5: Alternatif Çözüm - SendGrid

Gmail çalışmıyorsa, **SendGrid** kullanabilirsiniz:

1. https://sendgrid.com → Ücretsiz hesap oluşturun
2. API Key oluşturun
3. Render'da environment variables güncelleyin:

```
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
```

---

## 🔍 Debug Checklist

- [ ] Render loglarında "Email başarıyla gönderildi" görüyor musunuz?
- [ ] Environment variables'ların hepsi var mı?
- [ ] MAIL_PASSWORD doğru mu? (Gmail App Password)
- [ ] Gmail'de spam klasörünü kontrol ettiniz mi?
- [ ] Email adresi doğru mu? (typo olabilir)

---

## 🚨 Hala Çalışmıyorsa

Loglardaki **tam hata mesajını** paylaşın, birlikte çözelim!

