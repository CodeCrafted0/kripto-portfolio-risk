# 🔍 Database URL Bulma ve Ekleme - Detaylı Rehber

## Yöntem 1: Database Sayfasından (En Kolay)

1. **Render Dashboard'da** → Sol menüden database'inizi bulun
2. Database'e tıklayın
3. Sayfanın **üst kısmında** veya **"Info"** sekmesinde bakın
4. **"Internal Database URL"** veya **"Connection String"** yazısını arayın

## Yöntem 2: Connection String Formatı

Eğer Internal Database URL görmüyorsanız, şu bilgileri bulun:
- **Host** (database hostname)
- **Database** (database adı)
- **User** (kullanıcı adı)
- **Password** (şifre - genelde gösterilmez ama reset edilebilir)
- **Port** (genelde 5432)

Format: `postgres://USER:PASSWORD@HOST:PORT/DATABASE`

## Yöntem 3: Environment Group Kullan

Render'da database'ler genelde otomatik olarak aynı environment group'ta olan servislere bağlanır. Ama manuel eklemek daha iyi.

---

## 📋 Web Service'e Environment Variable Ekleme (Adım Adım)

### Adım 1: Web Service'e Gidin

1. **Render Dashboard** ana sayfasına gidin
2. **Sol menüden "kripto-portfolio-risk"** servisinize tıklayın
   - Veya servis listesinden bulun

### Adım 2: Settings Sekmesine Gidin

1. Servis sayfasında **üst menüden "Settings"** sekmesine tıklayın
2. (Sol menüde de "Settings" linki olabilir)

### Adım 3: Environment Variables Bölümünü Bulun

1. Settings sayfasında **aşağı kaydırın**
2. **"Environment Variables"** başlığını arayın
3. Veya **sağ menüden** "Environment" seçeneğine tıklayın

### Adım 4: Environment Variable Ekleyin

1. **"+ Add Environment Variable"** butonunu bulun
2. Tıklayın
3. **Key** alanına: `DATABASE_URL` yazın
4. **Value** alanına: Database URL'yi yapıştırın
5. **Save** veya **Add** butonuna tıklayın

---

## 🔍 Database URL Formatı Örneği

```
postgres://crypto_user:abc123xyz@dpg-xxxxx-a.frankfurt-postgres.render.com/crypto_risk_db
```

Veya Render'ın yeni formatı:
```
postgresql://crypto_user:abc123xyz@dpg-xxxxx-a.frankfurt-postgres.render.com/crypto_risk_db
```

---

## 💡 Eğer Hala Bulamıyorsanız

### Alternatif: Database'i Yeniden Oluştur (URL Göreceksiniz)

1. Mevcut database'i silin (eğer önemli veri yoksa)
2. Yeniden oluşturun
3. Oluşturma sırasında URL gösterilir

### Veya: Database Info Sayfasını Kontrol

Database sayfasında:
- **"Connections"** sekmesi
- **"Info"** sekmesi  
- **"Settings"** sekmesi

Hepsinin içinde URL olabilir.

---

## ⚠️ Önemli Not

Eğer Internal Database URL bulunamıyorsa:
- Database'iniz aynı "project" içindeyse, otomatik bağlanabilir
- Ama manuel eklemek daha garantili

**Şimdi Web Service → Settings → Environment Variables kısmına gidin ve DATABASE_URL eklemeyi deneyin!**

