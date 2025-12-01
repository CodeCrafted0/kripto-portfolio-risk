# 🚀 Platform Deployment (Yayınlama) Rehberi

## 🌐 Ücretsiz Hosting Seçenekleri

### 1. ✅ **Render.com** (ÖNERİLEN - En Kolay!)

**Avantajlar:**
- ✅ Tamamen ücretsiz
- ✅ Otomatik SSL sertifikası (HTTPS)
- ✅ Kolay deployment
- ✅ GitHub entegrasyonu
- ✅ Custom domain desteği

**Nasıl Deploy Edilir:**

1. **GitHub'a Yükleyin:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Render.com'a Kaydolun:**
   - https://render.com adresine gidin
   - GitHub hesabınızla giriş yapın

3. **Yeni Web Service Oluşturun:**
   - "New +" > "Web Service" tıklayın
   - GitHub repo'nuzu bağlayın
   - Ayarlar:
     - **Name:** kripto-portfolio-risk (istediğiniz isim)
     - **Environment:** Python 3
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `gunicorn app:app`
     - **Plan:** Free (ücretsiz)

4. **Environment Variables (Gerekirse):**
   - PORT otomatik atanır
   - BYBIT_API_KEY ve BYBIT_API_SECRET kullanıcılar kendi girecek

5. **Deploy!**
   - "Create Web Service" tıklayın
   - 5-10 dakika içinde hazır olur
   - URL: `https://kripto-portfolio-risk.onrender.com`

---

### 2. ✅ **Railway.app** (Çok Kolay!)

**Avantajlar:**
- ✅ Ücretsiz tier var ($5 kredi/ay)
- ✅ Çok hızlı deployment
- ✅ Otomatik HTTPS
- ✅ Database desteği

**Nasıl Deploy Edilir:**

1. **Railway'a Kaydolun:**
   - https://railway.app
   - GitHub ile giriş yapın

2. **Yeni Proje Oluşturun:**
   - "New Project" > "Deploy from GitHub repo"
   - Repo'nuzu seçin

3. **Otomatik Deploy:**
   - Railway otomatik algılar (Python projesi)
   - Otomatik deploy eder
   - URL verilir

---

### 3. ✅ **PythonAnywhere** (Basit)

**Avantajlar:**
- ✅ Tamamen ücretsiz (sınırlı)
- ✅ Python'a özel
- ✅ Kolay kurulum

**Nasıl Deploy Edilir:**

1. https://www.pythonanywhere.com kaydolun
2. Files > Upload files
3. Bash console'da:
   ```bash
   pip3.10 install --user flask flask-cors requests python-dotenv numpy
   ```
4. Web > Add a new web app
5. Flask > Python 3.10
6. WSGI file'ı düzenleyin
7. Reload!

---

## 💰 Ücretli (Daha Profesyonel) Seçenekler

### 4. **DigitalOcean Droplet**
- $4-6/ay
- Tam kontrol
- Daha hızlı

### 5. **AWS EC2**
- Pay-as-you-go
- Çok ölçeklenebilir
- Karmaşık kurulum

### 6. **Heroku**
- $7/ay (ücretsiz tier yok)
- Çok kolay
- Popüler

---

## 📋 Deployment İçin Gerekli Dosyalar

### 1. `Procfile` (Render/Railway için)
```
web: gunicorn app:app
```

### 2. `runtime.txt` (Python version)
```
python-3.10.0
```

### 3. `gunicorn` ekle (requirements.txt'e)
```
gunicorn==21.2.0
```

---

## 🔒 Güvenlik Notları

1. **API Key'ler:**
   - Kullanıcılar kendi API key'lerini girer
   - Server'da saklanmaz (session-based)

2. **HTTPS:**
   - Tüm modern hosting'ler otomatik HTTPS verir
   - Güvenli bağlantı

3. **Environment Variables:**
   - Hassas bilgileri .env'de saklayın
   - Git'e commit etmeyin (.gitignore'da var)

---

## 🎯 En İyi Seçenek: Render.com

**Neden Render.com?**
- ✅ Tamamen ücretsiz
- ✅ Otomatik HTTPS
- ✅ GitHub entegrasyonu
- ✅ Kolay deployment
- ✅ Custom domain
- ✅ 750 saat/ay ücretsiz (yeterli!)

**Adımlar:**
1. GitHub'a yükleyin
2. Render.com'a bağlayın
3. Deploy edin
4. Paylaşın! 🎉

---

## 📱 Domain Almak İsterseniz

1. **Namecheap** - $10-15/yıl
2. **GoDaddy** - $12-20/yıl
3. **Cloudflare** - En ucuz

Render.com'da custom domain ekleyebilirsiniz!

---

## 🚀 Hızlı Başlangıç (Render.com)

```bash
# 1. GitHub'a yükle
git init
git add .
git commit -m "Deploy ready"
git remote add origin https://github.com/kullaniciadi/repo.git
git push -u origin main

# 2. Render.com'da deploy et
# - GitHub repo'yu bağla
# - Web Service oluştur
# - Otomatik deploy!
```

5 dakikada canlı! 🎉

