# Oral Verification Demo Script

Bu script, canlı demo sırasında takip edilebilecek adımları içerir.

## Demo Hazırlığı

### 1. Terminal Hazırlığı
İki terminal penceresi açın:
- **Terminal 1:** Güvensiz versiyon için
- **Terminal 2:** Güvenli versiyon için

### 2. Uygulamaları Başlatma

**Terminal 1 - Güvensiz Versiyon:**
```bash
cd /Users/ege/Desktop/projects/SecurityProje
source venv/bin/activate
python3 app.py
```

**Terminal 2 - Güvenli Versiyon:**
```bash
cd /Users/ege/Desktop/projects/SecurityProje
source venv/bin/activate
python3 app_secure.py
```

## Demo Akışı (5-10 dakika)

### Bölüm 1: Uygulama Tanıtımı (1-2 dakika)

1. **Uygulama Açıklaması:**
   - "Bu bir Flask tabanlı kullanıcı giriş uygulamasıdır"
   - "SQLite veritabanı kullanıyor"
   - "Localhost'ta çalışıyor (127.0.0.1:5000)"

2. **Normal Kullanım Gösterimi:**
   - Tarayıcıda `http://127.0.0.1:5000` aç
   - Username: `admin` gir
   - Login butonuna tıkla
   - ✅ Başarılı giriş göster

### Bölüm 2: Güvenlik Açığının Tespiti (2-3 dakika)

1. **Kod İncelemesi:**
   - `app.py` dosyasını aç
   - Satır 67'yi göster: `query = f"SELECT * FROM users WHERE username = '{username}'"`
   - "Kullanıcı girdisi doğrudan SQL sorgusuna ekleniyor" açıkla

2. **Terminal Loglarını Göster:**
   - Terminal 1'deki logları göster
   - "Her sorgu terminalde görüntüleniyor" açıkla

### Bölüm 3: Exploit Gösterimi (2-3 dakika)

1. **SQL Injection Saldırısı:**
   - Username alanına: `' OR '1'='1` yaz
   - Login butonuna tıkla
   - ✅ Unauthorized access başarılı

2. **Terminal Analizi:**
   - Terminal 1'deki sorguyu göster:
     ```sql
     SELECT * FROM users WHERE username = '' OR '1'='1'
     ```
   - "Sorgu yapısı değiştirildi" açıkla
   - "WHERE clause her zaman TRUE döndürüyor" açıkla

3. **Etki Açıklaması:**
   - "Şifre olmadan admin hesabına erişim sağlandı"
   - "Bu bir kritik güvenlik açığı"

### Bölüm 4: Düzeltme Gösterimi (2-3 dakika)

1. **Güvenli Versiyona Geçiş:**
   - Tarayıcıda `http://127.0.0.1:5001` aç (güvenli versiyon)
   - `app_secure.py` dosyasını aç
   - Satır 67-68'i göster:
     ```python
     query = "SELECT * FROM users WHERE username = ?"
     cursor.execute(query, (username,))
     ```

2. **Parametreli Sorgu Açıklaması:**
   - "Query template ayrı, kullanıcı verisi parametre olarak geçiliyor"
   - "Kullanıcı girdisi kod olarak değil, veri olarak işleniyor"

3. **Aynı Saldırıyı Test Et:**
   - Username: `' OR '1'='1` yaz
   - Login butonuna tıkla
   - ❌ Saldırı başarısız

4. **Terminal Karşılaştırması:**
   - Terminal 2'deki logları göster
   - "Parameterized query kullanılıyor" mesajını göster
   - "Saldırı engellendi" açıkla

### Bölüm 5: Doğrulama ve Sonuç (1-2 dakika)

1. **Test Sonuçları Özeti:**
   - Güvensiz versiyon: SQL Injection başarılı
   - Güvenli versiyon: SQL Injection engellendi
   - Normal kullanım: Her iki versiyonda da çalışıyor

2. **Öğrenilen Dersler:**
   - "Parametreli sorgular kullanılmalı"
   - "Kullanıcı girdisi asla doğrudan sorguya eklenmemeli"
   - "Input validation önemli"

3. **Dokümantasyon Referansı:**
   - `VULNERABILITY_REPORT.md` - Detaylı analiz
   - `EXPLOIT_GUIDE.md` - Exploit adımları
   - `FIX_VERIFICATION.md` - Düzeltme doğrulaması

## Sorular ve Cevaplar (Hazırlık)

### Olası Sorular:

**S: Neden bu açık oluştu?**
C: Kullanıcı girdisi doğrudan string interpolation ile sorguya eklendi. Input validation ve parametreli sorgular kullanılmadı.

**S: Gerçek dünyada bu ne kadar yaygın?**
C: OWASP Top 10'da Injection (A03:2021) olarak listeleniyor. Çok yaygın bir açık türü.

**S: Başka hangi açıklar var?**
C: XSS, CSRF, Authentication bypass, Authorization issues gibi başka açıklar da olabilir.

**S: Sadece parametreli sorgu yeterli mi?**
C: Hayır, input validation, output encoding, least privilege prensibi de uygulanmalı.

## Demo İpuçları

1. ✅ Terminal loglarını büyük fontla göster
2. ✅ Kod satırlarını vurgula
3. ✅ Tarayıcı ve terminal'i yan yana göster
4. ✅ Her adımı açıkça açıkla
5. ✅ Sorulara hazırlıklı ol

## Zaman Yönetimi

- **Toplam:** 10 dakika
- **Tanıtım:** 2 dakika
- **Açık Tespiti:** 2 dakika
- **Exploit:** 3 dakika
- **Düzeltme:** 2 dakika
- **Sonuç:** 1 dakika

---

**İyi şanslar! 🍀**
