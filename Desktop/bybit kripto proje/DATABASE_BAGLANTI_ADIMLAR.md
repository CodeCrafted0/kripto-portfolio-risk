# 🔗 Database Bağlantı Adımları

## ✅ Database Oluşturuldu!

Şimdi yapılacaklar:

## 📋 Adım 1: Database URL'yi Alın

1. **Oluşturduğunuz PostgreSQL database'ine gidin**
   - Render Dashboard'da database'inize tıklayın
   - Veya sol menüden database'inizi bulun

2. **"Connections" veya "Info" sekmesine gidin**

3. **"Internal Database URL" değerini bulun**
   - Şu formatta olacak: `postgres://user:password@host:port/dbname`
   - **Bu URL'yi kopyalayın** (tümü)

## 📋 Adım 2: Web Service'e Environment Variable Ekleyin

1. **Web Service'inize gidin:**
   - Render Dashboard → **"kripto-portfolio-risk"** servisinize tıklayın

2. **Settings** sekmesine gidin

3. **"Environment"** veya **"Environment Variables"** bölümünü bulun

4. **"+ Add Environment Variable"** butonuna tıklayın

5. **Şu değerleri girin:**
   - **Key:** `DATABASE_URL`
   - **Value:** (Az önce kopyaladığınız Internal Database URL)

6. **Save** veya **Add** butonuna tıklayın

## 📋 Adım 3: Deploy Edin

1. **Manual Deploy** → **Deploy latest commit**
2. Database tabloları otomatik oluşturulacak

## ✅ Kontrol

Deploy sonrası logları kontrol edin:
- ✅ "Creating tables..." görünmeli
- ❌ Hata varsa paylaşın

---

**Şimdi Database URL'yi alıp Web Service'e ekleyin!** 🔗

