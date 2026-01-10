# 🛡️ SQL Injection Güvenlik Analizi Projesi

Bu proje, Vulnerability and Security dersi kapsamında, web uygulamalarındaki güvenlik açıklarını anlamak, simüle etmek ve analiz etmek amacıyla geliştirilmiştir.

## 🎯 Projenin Amacı

Bu çalışmanın temel amacı, siber güvenlik dünyasında en yaygın görülen saldırı türlerinden biri olan SQL Injection (SQLi) zafiyetini incelemektir. Proje şunları hedefler:

- Güvenli olmayan bir giriş sistemi kodlamak
- Arka planda çalışan veritabanı sorgularını terminal üzerinden canlı izlemek
- Basit bir saldırı vektörü (Payload) kullanarak sistemi bypass etmek (hacklemek)
- Güvenlik açığının neden kaynaklandığını ve nasıl kapatılacağını anlamak

## 🛠️ Gereksinimler ve Kurulum

Bu projeyi çalıştırmak için bilgisayarınızda Python yüklü olmalıdır.

### 1. Gerekli Kütüphanenin Yüklenmesi

Terminal veya Komut İstemi'ni (CMD) açın ve şu komutu çalıştırın:

```bash
pip install -r requirements.txt
```

veya

```bash
pip install flask
```

### 2. Uygulamanın Hazırlanması

Proje klasörüne gidin:

```bash
cd SecurityProje
```

## 🚀 Uygulamanın Çalıştırılması

### Güvensiz Versiyon (SQL Injection Açığı ile)

Terminali açın ve proje klasörüne giderek uygulamayı başlatın:

```bash
python app.py
```

Terminalde şu çıktıyı gördüğünüzde sunucu çalışıyor demektir:
```
Running on http://127.0.0.1:5000
```

Tarayıcınızdan `http://127.0.0.1:5000` adresine gidin.

### Güvenli Versiyon (Parametreli Sorgular ile)

Ayrı bir terminal penceresinde:

```bash
python app_secure.py
```

Bu versiyon `http://127.0.0.1:5001` adresinde çalışacaktır.

## ⚔️ Saldırı Senaryosu (Adım Adım)

Bu bölümde, sistemin nasıl kandırıldığını terminal kayıtları (loglar) üzerinden analiz edeceğiz.

### Adım 1: Normal Giriş Denemesi

1. İlk olarak sisteme rastgele bir isim girin (Örn: `Ahmet`).
2. Web Sitesi: "HATA: Kullanıcı bulunamadı" diyecektir.
3. Terminal Çıktısı:
   ```
   [!] Kullanıcının Yazdığı: Ahmet
   [!] Veritabanında Çalışan Kod: SELECT * FROM users WHERE username = 'Ahmet'
   ```

**Analiz:** Veritabanı sadece kullanıcı adı 'Ahmet' olanı aradı ve bulamadı. Her şey normal.

### Adım 2: SQL Injection Saldırısı (Hack)

1. Şimdi giriş kutusuna şu özel kodu (payload) yazın:
   ```
   ' OR '1'='1
   ```
2. Web Sitesi: "✅ BAŞARILI! Hoşgeldin admin" mesajı verecektir. Şifre girmeden içeri girdiniz!
3. Terminal Çıktısı (KRİTİK BÖLÜM):
   ```
   [!] Kullanıcının Yazdığı: ' OR '1'='1
   [!] Veritabanında Çalışan Kod: SELECT * FROM users WHERE username = '' OR '1'='1'
   ```

## 🧪 Neden Hacklendi? (Teknik Analiz)

Terminaldeki koda dikkat edin: `WHERE username = '' OR '1'='1'`

Bilgisayar bunu şöyle okur:

- Kullanıcı adı boş mu? (Hayır)
- **VEYA (OR)**
- 1 sayısı 1 sayısına eşit mi? (EVET, HER ZAMAN!)

Matematikte "1=1" her zaman doğru olduğu için, veritabanı bu sorguya "TRUE" (DOĞRU) cevabını verir ve ilk bulduğu kullanıcıyı (Admin) sisteme sokar.

## 🛡️ Çözüm ve Düzeltme (Patch)

Bu açığı kapatmak için veriyi doğrudan sorguya yapıştırmak yerine "Parameterized Queries" (Parametreli Sorgular) kullanılmalıdır.

### Hatalı Kod (Mevcut - app.py):

```python
# Kullanıcı ne yazarsa doğrudan koda dönüşüyor
query = f"SELECT * FROM users WHERE username = '{username}'"
cursor.execute(query)
```

### Güvenli Kod (Düzeltilmiş - app_secure.py):

```python
# Kullanıcı verisi sadece 'veri' olarak işlenir, kod olarak çalıştırılmaz
query = "SELECT * FROM users WHERE username = ?"
cursor.execute(query, (username,))
```

## 📁 Proje Yapısı

```
SecurityProje/
├── app.py                 # Güvensiz versiyon (SQL Injection açığı ile)
├── app_secure.py          # Güvenli versiyon (Parametreli sorgular ile)
├── init_db.py             # Veritabanı başlatma scripti
├── requirements.txt       # Python bağımlılıkları
├── README.md             # Bu dosya
├── users.db              # Güvensiz versiyon veritabanı (otomatik oluşur)
├── users_secure.db       # Güvenli versiyon veritabanı (otomatik oluşur)
└── templates/
    ├── index.html        # Güvensiz versiyon ana sayfa
    ├── result.html       # Güvensiz versiyon sonuç sayfası
    ├── index_secure.html # Güvenli versiyon ana sayfa
    └── result_secure.html # Güvenli versiyon sonuç sayfası
```

## 🧪 Test Senaryoları

### Senaryo 1: Normal Kullanıcı Girişi
- **Input:** `admin`
- **Beklenen:** Başarılı giriş (admin kullanıcısı mevcut)

### Senaryo 2: Geçersiz Kullanıcı
- **Input:** `Ahmet`
- **Beklenen:** Hata mesajı (kullanıcı bulunamadı)

### Senaryo 3: SQL Injection Saldırısı (Güvensiz Versiyon)
- **Input:** `' OR '1'='1`
- **Beklenen:** Başarılı giriş (SQL Injection başarılı)
- **Güvenli Versiyon:** Hata mesajı (SQL Injection engellendi)

### Senaryo 4: Diğer SQL Injection Payload'ları
- `' OR '1'='1' --`
- `admin' --`
- `' UNION SELECT * FROM users --`

## 📝 Sonuç

Bu proje ile, kullanıcıdan alınan verilerin kontrol edilmeden (sanitize edilmeden) veritabanı sorgularına eklenmesinin ne kadar tehlikeli olduğu görülmüştür. Basit bir manipülasyon ile yönetici hakları ele geçirilebilir. Güvenlik için her zaman girdi denetimi ve parametreli sorgular kullanılmalıdır.

## ⚠️ Önemli Uyarı

Bu proje **sadece eğitim amaçlı** geliştirilmiştir. Bu kodları production ortamında kullanmayın. Gerçek uygulamalarda:

1. Parametreli sorgular kullanın
2. Input validation yapın
3. SQL Injection koruması sağlayın
4. Güvenlik testleri yapın
5. Düzenli güvenlik güncellemeleri yapın

## 📚 Ek Kaynaklar

- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [SQLite Parameterized Queries](https://docs.python.org/3/library/sqlite3.html)

## 👨‍💻 Geliştirici

Bu proje Vulnerability and Security dersi kapsamında geliştirilmiştir.

---

**Not:** Bu projeyi çalıştırmadan önce `init_db.py` scriptini çalıştırarak veritabanını başlatabilirsiniz, ancak `app.py` ve `app_secure.py` dosyaları otomatik olarak veritabanını oluşturur.

