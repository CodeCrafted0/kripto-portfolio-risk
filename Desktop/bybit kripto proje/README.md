# 🔐 Kripto Portföy Risk Analiz Platformu

Akıllı kripto portföy analizi ve risk yönetim platformu. Bybit API ile entegre, gerçek zamanlı analiz yapan bir araç.

## ✨ Özellikler

### 📊 Portföy Analizi
- **Portföy Risk Skoru**: Otomatik risk hesaplama (1-100 arası)
- **Diversifikasyon Analizi**: Varlık dağılımı ve konsantrasyon analizi
- **Volatilite Hesaplama**: Her coin için volatilite skoru
- **Korelasyon Analizi**: Coinler arası ilişki analizi
- **Rebalancing Önerileri**: Akıllı portföy dengeleme tavsiyeleri
- **Gerçek Zamanlı Fiyatlar**: Bybit API ile canlı fiyat takibi

### ⚠️ Kaldıraç (Leverage) Analizi - YENİ!
- **Kaldıraç Risk Uyarıları**: Yüksek kaldıraç kullanımı için kritik uyarılar
- **Liquidation Risk Analizi**: Pozisyonların liquidation riskini hesaplar
- **Margin Kullanım Takibi**: Margin kullanım yüzdesi ve uyarıları
- **Pozisyon Bazlı Risk Skorları**: Her pozisyon için detaylı risk analizi
- **Güvenli Margin Limit Önerileri**: Maksimum margin kullanım önerileri

### 🎯 Pozisyon Boyutu (Position Sizing) - YENİ!
- **Optimal Pozisyon Hesaplama**: Risk toleransına göre optimal pozisyon boyutu
- **Risk Bazlı Hesaplama**: Hesabın belirli yüzdesi kadar risk almayı sağlar
- **Stop-Loss Entegrasyonu**: Stop-loss ile pozisyon boyutu hesaplama
- **Risk Profili Desteği**: Konservatif, dengeli, agresif profiller
- **Kaldıraç Kontrolü**: Risk profiline göre maksimum kaldıraç limitleri

### 💡 Stop-Loss ve Risk/Reward - YENİ!
- **Stop-Loss Önerileri**: Maksimum zarar limitine göre stop-loss önerisi
- **Risk/Reward Hesaplama**: İşlem açmadan önce risk/reward oranı analizi
- **İşlem Değerlendirme**: Risk/reward oranına göre işlem kalitesi değerlendirmesi

### 🎨 Profesyonel Web Arayüzü
- Modern ve kullanıcı dostu dashboard
- Gerçek zamanlı analiz sonuçları
- Detaylı görselleştirmeler
- Responsive tasarım

## 🚀 Kurulum

```bash
pip install -r requirements.txt
```

## ⚙️ Yapılandırma

`.env` dosyası oluşturun:

```
BYBIT_API_KEY=your_api_key
BYBIT_API_SECRET=your_api_secret
```

## 📖 Kullanım

```bash
python app.py
```

Tarayıcıda: `http://localhost:5000`

## 💰 Monetizasyon Fikirleri

1. **Freemium Model**: Temel analiz ücretsiz, gelişmiş özellikler ücretli
2. **API Servisi**: Diğer uygulamalara analiz servisi satışı
3. **Affiliate**: Kripto borsalarına yönlendirme komisyonu
4. **Premium Abonelik**: Gelişmiş özellikler, özel raporlar
5. **White-label**: Başka şirketlere lisanslama

## 🛠️ Teknolojiler

- **Backend**: Python Flask
- **API**: Bybit REST API
- **Frontend**: HTML5, JavaScript, Bootstrap 5
- **Görselleştirme**: Chart.js (opsiyonel)

## 📋 Kullanım Senaryoları

### 1. Portföy Risk Analizi
Portföyünüzü girin, otomatik risk skoru ve detaylı analiz alın.

### 2. Kaldıraçlı İşlem Kontrolü
Kaldıraçlı pozisyonlarınızın risklerini görün, liquidation uyarıları alın.

### 3. Yeni Pozisyon Açmadan Önce
Optimal pozisyon boyutunu hesaplayın, risk/reward oranını kontrol edin.

### 4. Stop-Loss Belirleme
Maksimum zarar limitinize göre otomatik stop-loss önerisi alın.

## ⚠️ Önemli Uyarılar

- Bu araç **sadece analiz amaçlıdır**, yatırım tavsiyesi değildir
- Kripto yatırımları yüksek risklidir, sermayenizi kaybedebilirsiniz
- Kaldıraçlı işlemler çok tehlikelidir, profesyoneller bile dikkatli kullanır
- Her zaman stop-loss kullanın ve risk yönetimi kurallarına uyun

## 🚧 Geliştirme Durumu

✅ Portföy risk analizi  
✅ Kaldıraç analizi  
✅ Pozisyon boyutu hesaplama  
✅ Stop-loss önerileri  
✅ Risk/Reward hesaplama  
✅ Profesyonel web arayüzü  
🔄 Gerçek zamanlı fiyat güncellemeleri (geliştirme aşamasında)  
🔄 API key ile Bybit entegrasyonu (opsiyonel)

