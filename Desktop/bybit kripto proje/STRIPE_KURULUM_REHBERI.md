# 💳 Stripe Kurulum Rehberi - Gelir Elde Etmek İçin

## 🎯 Nasıl Gelir Elde Edeceğiz?

### Gelir Modeli
1. **Kullanıcılar** → Fiyatlandırma sayfasına gelir
2. **Plan seçer** → Starter ($9.99/ay) veya Pro ($29.99/ay)
3. **Stripe Checkout** → Ödeme yapar
4. **Webhook** → Abonelik aktif edilir
5. **Aylık gelir** → Otomatik tahsilat

### Beklenen Gelir
- **İlk ay**: 10 kullanıcı × $10 = **$100/ay**
- **3. ay**: 50 kullanıcı × $10 = **$500/ay**
- **6. ay**: 100 kullanıcı × $15 = **$1,500/ay**
- **12. ay**: 500 kullanıcı × $20 = **$10,000/ay**

---

## 🔧 Stripe Kurulum Adımları

### Adım 1: Stripe Hesabı Oluştur

1. **https://stripe.com** → **Sign up**
2. **Email ve şifre** ile kayıt ol
3. **Test mode**'da başla (ücretsiz, gerçek para yok)
4. **Dashboard**'a git

### Adım 2: API Keys Al

1. Stripe Dashboard → **Developers** → **API keys**
2. **Test mode**'da olduğundan emin ol
3. **Publishable key** kopyala (pk_test_... ile başlar)
4. **Secret key** kopyala (sk_test_... ile başlar)
   - ⚠️ Secret key'i kimseyle paylaşma!

### Adım 3: Webhook Secret Al

1. Stripe Dashboard → **Developers** → **Webhooks**
2. **Add endpoint** butonuna tıkla
3. **Endpoint URL**: `https://kripto-portfolio-risk.onrender.com/payment/webhook`
4. **Events to send**: Şunları seç:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. **Add endpoint** → **Signing secret** kopyala (whsec_... ile başlar)

### Adım 4: Render'da Environment Variables Ekle

1. **Render Dashboard** → **kripto-portfolio-risk** servisi
2. **Settings** → **Environment Variables**
3. Şu değişkenleri ekle:

```
STRIPE_SECRET_KEY=sk_test_... (Secret key)
STRIPE_PUBLISHABLE_KEY=pk_test_... (Publishable key)
STRIPE_WEBHOOK_SECRET=whsec_... (Webhook secret)
```

### Adım 5: Deploy ve Test

1. **Deploy** et (otomatik olacak)
2. **Fiyatlandırma sayfasına** git: `/pricing`
3. **Test kartı** ile ödeme yap:
   - Kart: `4242 4242 4242 4242`
   - Tarih: Herhangi bir gelecek tarih
   - CVC: Herhangi bir 3 haneli sayı
   - ZIP: Herhangi bir 5 haneli sayı

---

## ✅ Kontrol Listesi

- [ ] Stripe hesabı oluşturuldu
- [ ] API keys alındı (Publishable + Secret)
- [ ] Webhook endpoint oluşturuldu
- [ ] Webhook secret alındı
- [ ] Render'da 3 environment variable eklendi
- [ ] Deploy edildi
- [ ] Test ödemesi yapıldı

---

## 🚀 Production'a Geçiş

### Test Mode'dan Live Mode'a

1. Stripe Dashboard → **Activate account**
2. **Business bilgileri** gir (şirket adı, vergi numarası, vb.)
3. **Bank account** ekle (para çekmek için)
4. **Live mode**'a geç
5. **Live API keys** al
6. Render'da environment variables'ı güncelle:
   - `STRIPE_SECRET_KEY` → Live secret key
   - `STRIPE_PUBLISHABLE_KEY` → Live publishable key
   - `STRIPE_WEBHOOK_SECRET` → Live webhook secret

---

## 💰 Para Çekme

1. Stripe Dashboard → **Payments** → **Transfers**
2. **Transfer** butonuna tıkla
3. Miktar gir
4. Bank account'a para gönderilir (2-3 iş günü)

---

## 📊 Gelir Takibi

1. Stripe Dashboard → **Payments** → Tüm ödemeleri gör
2. **Customers** → Abone kullanıcıları gör
3. **Subscriptions** → Aktif abonelikleri gör
4. **Analytics** → Gelir grafikleri

---

## 🎯 Sonuç

**Stripe kurulumu tamamlandığında:**
- ✅ Kullanıcılar ödeme yapabilir
- ✅ Abonelikler otomatik yönetilir
- ✅ Aylık gelir üretmeye başlarız
- ✅ Para banka hesabına çekilebilir

**Şimdi yapılacaklar:**
1. Stripe hesabı oluştur
2. API keys al
3. Render'da environment variables ekle
4. Test et!

**Sorularınız varsa sorun!** 🚀

