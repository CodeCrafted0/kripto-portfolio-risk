# 🔑 Bybit API Key Oluşturma - Adım Adım Rehber

## ✅ Şu Anki Durumunuz (Doğru!)

Gördüğüm kadarıyla:
- ✅ **API Transaction** seçilmiş (Doğru)
- ✅ **Read-Only** seçilmiş (Mükemmel! ✅)
- ⚠️ **No IP restriction** seçilmiş (Güvenlik için IP eklemeniz önerilir)

---

## 📋 ŞİMDİ YAPMANIZ GEREKENLER

### ADIM 1: İzinleri Seçin (ÇOK ÖNEMLİ!)

Aşağıdaki **check box'ları işaretleyin**:

#### 1️⃣ **Unified Trading > Contract > Positions**
- ☑️ **Positions** checkbox'ını işaretleyin
- Açıklama: "Query positions info and filled orders for Derivatives trading only"
- **Bu bizim için EN ÖNEMLİSİ!** Futures pozisyonlarınızı görmek için gerekli.

#### 2️⃣ **Unified Trading > SPOT > Trade**
- ☑️ **Trade** checkbox'ını işaretleyin
- Açıklama: "Query order info for Spot trading only"
- Spot pozisyonlarınızı görmek için gerekli.

#### 3️⃣ **Assets > Wallet > Account Transfer**
- ☑️ **Account Transfer** checkbox'ını işaretleyin
- Açıklama: "Query asset transfer records"
- Bakiye bilgilerini görmek için gerekli.

### ✅ İsteğe Bağlı (Ama Önerilen):

#### 4️⃣ **Unified Trading > Contract > Orders**
- ☑️ **Orders** checkbox'ını işaretleyin
- Açıklama: "Query order info for Derivatives trading only"
- İşlem geçmişinizi görmek için.

---

### ADIM 2: IP Kısıtlaması Ekleyin (GÜVENLİK!)

**⚠️ ÖNEMLİ UYARI:**
Sayfada yazıyor: "If an API key isn't linked to an IP address, it will expire in 3 months."

**Ne Yapmalısınız:**

1. **"Only IPs with permissions granted are allowed to access the OpenAPI"** seçeneğini işaretleyin

2. Kendi IP adresinizi öğrenin:
   - Google'da "what is my ip" yazın
   - Veya şu adrese gidin: https://www.whatismyip.com/

3. IP adresinizi kutuya yazın (örnek: `192.168.1.100`)

4. Birden fazla yerden erişecekseniz, virgülle ayırarak ekleyin:
   ```
   123.45.67.89,98.76.54.32
   ```

**Not:** Eğer IP adresiniz değişiyorsa (dinamik IP), "No IP restriction" bırakabilirsiniz ama 3 ay sonra yeniden oluşturmanız gerekecek.

---

### ADIM 3: Submit Butonuna Tıklayın

Tüm izinleri seçtikten sonra:
1. Sayfayı aşağı kaydırın
2. **"Submit"** (Turuncu buton) tıklayın
3. API Key ve Secret Key'i güvenli bir yere kopyalayın!

---

## 📝 ÖZET - Hangi Checkbox'ları İşaretlemeli?

### ✅ MUTLAKA İŞARETLEYİN:
```
☑️ Unified Trading > Contract > Positions
☑️ Unified Trading > SPOT > Trade  
☑️ Assets > Wallet > Account Transfer
```

### 💡 İSTEĞE BAĞLI:
```
☑️ Unified Trading > Contract > Orders (İşlem geçmişi için)
```

### ❌ İŞARETLEMEYİN:
```
❌ Unified Trading > Contract > Orders (sadece detaylı analiz için)
❌ Assets > Wallet > Withdrawal (Zaten Read-Only desteklenmiyor)
❌ Fiat trading, Earn, Bybit Pay (Gerekmez)
```

---

## ⚠️ GÜVENLİK İPUÇLARI

1. **IP Kısıtlaması Ekleyin**
   - API key'inizin başkaları tarafından kullanılmasını önler
   - 3 ay sonra expire olmaz

2. **Sadece Read-Only İzinleri Verin**
   - Zaten seçmişsiniz, mükemmel! ✅
   - Hiçbir yazma izni (Write) vermeyin

3. **API Key'i Güvenli Tutun**
   - Secret Key sadece bir kez gösterilir!
   - Ekran görüntüsü alıp güvenli bir yere kaydedin
   - Başkalarıyla paylaşmayın

---

## 🚀 SONRAKI ADIMLAR

1. ✅ İzinleri seçin (yukarıdaki checkbox'lar)
2. ✅ IP adresinizi ekleyin (güvenlik için)
3. ✅ Submit'e tıklayın
4. ✅ API Key ve Secret Key'i kopyalayın
5. ✅ Platformumuzda kullanın!

---

## 📞 Sorun mu var?

- "Positions" checkbox'ını göremiyorsanız: Sayfayı aşağı kaydırın
- IP adresinizi bilmiyorsanız: Google'da "what is my ip" yazın
- Başka bir sorun: Bana yazın!

