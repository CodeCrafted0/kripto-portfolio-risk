# 🔧 API Bağlantı Hataları ve Çözümleri

## ❌ "API bağlantı başarısız" Hatası

### Olası Nedenler ve Çözümler:

### 1. ❌ Geçersiz API Key (Hata Kodu: 10003)

**Sorun:** API Key yanlış veya geçersiz.

**Çözüm:**
- ✅ Bybit API Management sayfasında API Key'inizi kontrol edin
- ✅ API Key'i tam olarak kopyaladığınızdan emin olun (başında/sonunda boşluk olmamalı)
- ✅ API Key'in aktif olduğunu kontrol edin
- ✅ Yeni bir API Key oluşturmayı deneyin

---

### 2. ❌ Yanlış Signature (Hata Kodu: 10004)

**Sorun:** API Secret yanlış veya signature hesaplama hatası.

**Çözüm:**
- ✅ API Secret'ınızı kontrol edin (tam olarak kopyalandığından emin olun)
- ✅ Başında veya sonunda boşluk olmadığından emin olun
- ✅ Secret Key'i tekrar kopyalayın (Bybit'ten)
- ✅ System-generated API Keys kullandığınızdan emin olun (RSA değil!)

---

### 3. ❌ IP Adresi Kısıtlaması (Hata Kodu: 10006)

**Sorun:** IP adresiniz whitelist'te değil.

**Çözüm:**
1. **Kendi IP'nizi öğrenin:**
   - Google'da "what is my ip" yazın
   - Veya şu adrese gidin: https://www.whatismyip.com/

2. **Bybit'te IP ekleyin:**
   - Bybit API Management sayfasına gidin
   - API Key'inizin yanındaki "Edit" butonuna tıklayın
   - "IP Whitelist" bölümüne kendi IP'nizi ekleyin
   - Kaydedin

3. **Alternatif:** IP kısıtlamasını geçici olarak kaldırın (daha az güvenli)

**Not:** IP kısıtlaması yoksa, API key 3 ay sonra expire olur!

---

### 4. ❌ İzinler Yetersiz (Hata Kodu: 33004)

**Sorun:** API Key'in yeterli izinleri yok.

**Çözüm - Şu İzinleri Ekleyin:**

1. **Unified Trading > Contract > Positions**
   - ☑️ Positions checkbox'ını işaretleyin

2. **Unified Trading > SPOT > Trade**
   - ☑️ Trade checkbox'ını işaretleyin

3. **Assets > Wallet > Account Transfer**
   - ☑️ Account Transfer checkbox'ını işaretleyin

**Nasıl Düzeltilir:**
- Bybit API Management sayfasına gidin
- API Key'inizin yanındaki "Edit" butonuna tıklayın
- Yukarıdaki izinleri ekleyin
- Kaydedin

---

### 5. ❌ API Key Süresi Dolmuş

**Sorun:** API Key 3 ay sonra expire olmuş (IP kısıtlaması yoksa).

**Çözüm:**
- ✅ Yeni bir API Key oluşturun
- ✅ Bu sefer IP kısıtlaması ekleyin (böylece expire olmaz)

---

### 6. ❌ Yanlış API Key Tipi

**Sorun:** Self-generated API Keys (RSA) kullanıyorsunuz.

**Çözüm:**
- ✅ System-generated API Keys (HMAC) kullanın
- ✅ Yeni bir API Key oluştururken "System-generated" seçin

---

## 🔍 Hata Ayıklama Adımları

### Adım 1: API Key'leri Kontrol Edin
```
✅ API Key boşluk içermiyor mu?
✅ API Secret boşluk içermiyor mu?
✅ Doğru kopyalanmış mı?
```

### Adım 2: Bybit'te Kontrol Edin
```
✅ API Key aktif mi?
✅ Read izinleri var mı?
✅ IP kısıtlaması doğru mu?
✅ System-generated (HMAC) mi?
```

### Adım 3: Test Edin
1. Bybit API Management sayfasında API Key'inizi kontrol edin
2. Platformumuzda tekrar bağlanmayı deneyin
3. Hata mesajını okuyun ve yukarıdaki çözümlere bakın

---

## 📋 Hızlı Kontrol Listesi

Bağlantı hatası alıyorsanız şunları kontrol edin:

- [ ] API Key doğru kopyalandı mı?
- [ ] API Secret doğru kopyalandı mı?
- [ ] System-generated API Keys kullanıyorum mu?
- [ ] "Read" izinleri var mı?
- [ ] IP kısıtlaması doğru mu? (veya kaldırıldı mı?)
- [ ] API Key aktif mi?
- [ ] API Key süresi dolmamış mı?

---

## 💡 Yaygın Hatalar

1. **API Key sonunda boşluk var**
   - Çözüm: Tekrar kopyalayın, sonundaki boşluğu silin

2. **Secret Key yanlış kopyalandı**
   - Çözüm: Bybit'ten tekrar kopyalayın

3. **IP adresi değişmiş**
   - Çözüm: Yeni IP'nizi whitelist'e ekleyin

4. **İzinler eksik**
   - Çözüm: Unified Trading > Contract > Positions ekleyin

5. **RSA API Key kullanılıyor**
   - Çözüm: System-generated (HMAC) kullanın

---

## 🆘 Hala Çözülemedi mi?

Eğer yukarıdaki çözümler işe yaramadıysa:

1. Yeni bir API Key oluşturun
2. Şu ayarlarla oluşturun:
   - System-generated (HMAC) ✅
   - Read-Only ✅
   - IP kısıtlaması: Kendi IP'niz ✅
   - İzinler: Positions, Trade, Account Transfer ✅

3. Yeni key'lerle tekrar deneyin

