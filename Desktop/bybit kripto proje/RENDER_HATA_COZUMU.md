# 🔧 Render Build Hatası - Çözüm

## ❌ Hata Mesajı
```
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
```

## 🔍 Sorun Analizi

Render build sırasında `requirements.txt` dosyasını bulamıyor. Bu genellikle şu nedenlerden olur:

1. **Root Directory ayarı yanlış** - Render'da servis ayarlarında "Root Directory" boş olmalı veya "." olmalı
2. **Python versiyonu** - Render 3.13.4 kullanıyor ama 3.10.12 olmalı

## ✅ Çözüm Adımları

### Render Dashboard'da Yapılacaklar:

1. **Servisinize gidin:** "kripto-portfolio-risk"
2. **"Settings" (Ayarlar) sekmesine tıklayın**
3. **Şu ayarları kontrol edin:**

#### Root Directory Ayarı:
- **Root Directory:** Boş bırakın VEYA `.` yazın
- Bu alan boş olmalı, çünkü dosyalar repo'nun root'unda

#### Build & Start Commands:
- **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`

#### Environment:
- **Environment:** Python 3
- **Python Version:** `3.10.12` (runtime.txt dosyasından otomatik okunur)

4. **"Save Changes" butonuna tıklayın**
5. **"Manual Deploy" > "Deploy latest commit" ile tekrar deploy edin**

## 📋 Kontrol Listesi

Render Settings'te kontrol edin:
- [ ] Root Directory: BOŞ veya `.`
- [ ] Build Command: `pip install --upgrade pip && pip install -r requirements.txt`
- [ ] Start Command: `gunicorn app:app`
- [ ] Environment: Python 3
- [ ] Python Version: 3.10.12 (runtime.txt otomatik kullanılır)

## 🎯 Önemli Not

**Root Directory alanı boş olmalı!** Eğer bu alan doluysa veya yanlış bir path varsa, Render dosyaları yanlış yerde arar ve `requirements.txt` bulunamaz.

## 📝 Alternatif Çözüm

Eğer hala çalışmazsa, Render'da servisi silip yeniden oluşturun ve root directory'yi BOŞ bırakın.

