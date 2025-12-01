# 🔑 Bybit API Key Kurulum Rehberi

## Hangi API Key Tipini Seçmeliyim?

### ✅ **System-generated API Keys (HMAC)** - ÖNERİLEN

**Neden?**
- Kodumuz **HMAC SHA256** signature kullanıyor
- Daha kolay kurulum
- Bybit tarafından otomatik oluşturulur
- Hemen kullanılabilir

**Nasıl Oluşturulur:**
1. Bybit hesabınıza giriş yapın
2. API Management sayfasına gidin
3. "Create New Key" butonuna tıklayın
4. **"System-generated API Keys"** seçeneğini seçin
5. API Key adı verin (örn: "Risk Analiz Platformu")
6. İzinleri seçin:
   - ✅ **Read** (Zorunlu - Pozisyonları okumak için)
   - ❌ **Write** (GEREKMEZ - Sadece okuma yapıyoruz)
   - ❌ **Withdraw** (GEREKMEZ - Hiçbir para transferi yapmıyoruz)
7. API Key ve Secret Key'i kopyalayın
8. Platformumuzda kullanın

### ❌ Self-generated API Keys (RSA) - KULLANMAYIN

- RSA encryption kullanır
- Kodumuz HMAC kullandığı için uyumsuz
- Daha karmaşık kurulum gerektirir

---

## 🔐 Güvenlik Ayarları

### Önemli Güvenlik İpuçları:

1. **IP Kısıtlaması Ekleyin**
   - Sadece kendi IP adresinizden erişilebilir yapın
   - Daha fazla güvenlik için

2. **Sadece Gerekli İzinleri Verin**
   - ✅ **Read** - Sadece bu izin yeterli
   - ❌ **Write** - GEREKMEZ (işlem yapmıyoruz)
   - ❌ **Withdraw** - GEREKMEZ (para çekmiyoruz)

3. **API Key'i Güvenli Tutun**
   - Başkalarıyla paylaşmayın
   - Ekran görüntüsü almayın
   - Güvenli bir yerde saklayın

4. **Düzenli Kontrol Edin**
   - Bybit'te API key kullanımınızı kontrol edin
   - Şüpheli aktivite görürseniz hemen iptal edin

---

## 📋 API Key Oluşturma Adımları

### Adım 1: Bybit'e Giriş Yapın
- https://www.bybit.com adresine gidin
- Hesabınıza giriş yapın

### Adım 2: API Management Sayfasına Gidin
- Sağ üst köşede profil simgenize tıklayın
- "API" veya "API Management" seçin
- Veya direkt: https://www.bybit.com/app/user/api-management

### Adım 3: Yeni API Key Oluşturun
- "Create New Key" butonuna tıklayın
- **"System-generated API Keys"** seçin
- API Key için bir isim verin (örn: "Risk Analiz Tool")

### Adım 4: İzinleri Ayarlayın
- **Read** iznini aktif edin ✅
- **Write** ve **Withdraw** izinlerini KAPALI bırakın ❌

### Adım 5: IP Kısıtlaması (Opsiyonel ama Önerilen)
- Kendi IP adresinizi ekleyin
- Sadece bu IP'den erişilebilir olacak

### Adım 6: API Key'leri Kopyalayın
- **API Key** ve **Secret Key**'i güvenli bir yere kopyalayın
- ⚠️ Secret Key sadece bir kez gösterilir! Kaydedin!

### Adım 7: Platformumuzda Kullanın
- Platformumuzda "Bybit Entegrasyonu" sekmesine gidin
- API Key ve Secret Key'i girin
- "Bağlan" butonuna tıklayın

---

## ⚠️ Sorun Giderme

### "API bağlantısı başarısız" hatası alıyorum
- ✅ API Key ve Secret Key'in doğru olduğundan emin olun
- ✅ "Read" izninin aktif olduğunu kontrol edin
- ✅ IP kısıtlaması varsa, kendi IP'nizin eklendiğini kontrol edin
- ✅ API Key'in aktif olduğunu kontrol edin

### "Pozisyonlar çekilemiyor" hatası
- ✅ Hesabınızda açık pozisyon var mı kontrol edin
- ✅ API Key'in "Read" iznine sahip olduğunu kontrol edin
- ✅ Unified account kullanıyorsanız, pozisyonların görünür olduğundan emin olun

---

## 🔄 API v3 vs v5

Kodumuz **API v5** kullanıyor. Eğer Bybit'te API versiyonu seçeneği varsa:
- ✅ **API v5** seçin
- ❌ API v3 kullanmayın (eski versiyon)

---

## 📝 Örnek İzin Ayarları

**Güvenli Konfigürasyon:**
```
✅ Read Only - Aktif
❌ Read & Write - Kapalı
❌ Withdraw - Kapalı
✅ IP Whitelist - Kendi IP'niz
```

Bu ayarlar platformumuzun çalışması için yeterlidir ve maksimum güvenlik sağlar!

