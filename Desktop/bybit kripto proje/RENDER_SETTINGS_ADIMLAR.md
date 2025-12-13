# 🔧 Render Settings - Adım Adım Rehber

## ⚠️ ÖNEMLİ: Doğru Sayfaya Gidin!

Şu anda **"Environment"** sayfasındasınız. Ama Root Directory, Build Command gibi ayarlar **"Settings"** sayfasında!

## 📍 Settings Sayfasına Nasıl Gidilir?

1. **Sol menüde (sidebar) "Settings" yazısına tıklayın**
   - "Environment" seçeneğinin HEMEN ÜSTÜNDE
   - Mor renkli olmayan, normal bir link olacak

2. **Settings sayfası açılacak**

## ⚙️ Settings Sayfasında Yapılacaklar

Settings sayfasında şu bölümleri bulacaksınız:

### 1. Root Directory
- **Kontrol edin:** Bu alan **BOŞ** olmalı
- Eğer bir şey yazıyorsa, **SİLİN ve boş bırakın**
- ❌ YANLIŞ: `/` veya `./` veya başka bir path
- ✅ DOĞRU: (Tamamen boş, hiçbir şey yazmayın)

### 2. Build Command
- Şu komut olmalı:
  ```
  pip install --upgrade pip && pip install -r requirements.txt
  ```
- Eğer farklıysa, düzeltin

### 3. Start Command
- Şu komut olmalı:
  ```
  gunicorn app:app
  ```
- Eğer farklıysa, düzeltin

### 4. Environment
- **Environment:** `Python 3` seçili olmalı
- **Python Version:** `3.10.12` (runtime.txt dosyasından otomatik okunur)

### 5. Değişiklikleri Kaydedin
- **En alta kaydırın**
- **"Save Changes"** butonuna tıklayın

## 🎯 Özet: Hangi Butona Tıklayacaksınız?

1. **Sol menüde "Settings"** yazısına tıklayın (Environment'ın üstünde)
2. **Root Directory** alanını kontrol edin (boş olmalı)
3. **Build Command** ve **Start Command** kontrol edin
4. **"Save Changes"** butonuna tıklayın
5. **"Manual Deploy"** → **"Deploy latest commit"**

## 🔍 Settings Sayfasını Bulamıyorsanız

Sol menüde şunları göreceksiniz:
- Events
- **Settings** ← BURAYA TIKLAYIN
- Logs (MONITOR altında)
- Metrics (MONITOR altında)
- Environment (MANAGE altında) ← ŞU AN BURADASINIZ
- Shell (MANAGE altında)
- ...

"Settings" direkt "Events"in altında, "MONITOR" bölümünün üstünde olmalı.

---

**Şimdi sol menüden "Settings" yazısına tıklayın!** 👈

