"""
Restoran Menü Sistemi - SQL Injection Açığı ile
Bu uygulama, restoran menü sistemini simüle eder ve SQL Injection açığını gösterir.
UYARI: Bu kod kasıtlı güvenlik açıkları içerir. Production'da kullanmayın!
"""

# Flask ve diğer gerekli kütüphaneleri import et
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
from datetime import datetime

# Flask uygulamasını oluştur
app = Flask(__name__)
# Session güvenliği için secret key (production'da değiştirilmeli)
app.secret_key = 'demo_secret_key_change_in_production'

# Veritabanı dosya yolu
DB_FILE = 'restaurant.db'

def init_database():
    """
    Veritabanını başlatır ve örnek verilerle doldurur.
    Eğer veritabanı zaten varsa ve veriler mevcutsa, yeni veri eklemez.
    """
    # Veritabanı bağlantısını oluştur
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Kullanıcılar tablosunu oluştur
    # id: Benzersiz kullanıcı kimliği
    # username: Kullanıcı adı (benzersiz, boş olamaz)
    # password: Şifre (boş olamaz)
    # role: Kullanıcı rolü (customer, employee, admin)
    # full_name: Kullanıcının tam adı
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'customer',
            full_name TEXT
        )
    ''')
    
    # Menü öğeleri tablosunu oluştur
    # id: Benzersiz menü öğesi kimliği
    # name: Yemek adı
    # category: Kategori (Pizza, Pasta, Salata, vb.)
    # price: Fiyat
    # description: Açıklama
    # image_url: Emoji veya görsel URL
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            image_url TEXT
        )
    ''')
    
    # Müşteriler tablosunu oluştur
    # user_id: Kullanıcı tablosuna referans
    # name: Müşteri adı
    # email: E-posta adresi (benzersiz)
    # phone: Telefon numarası
    # address: Adres bilgisi
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            address TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Siparişler tablosunu oluştur
    # customer_id: Müşteri tablosuna referans
    # item_id: Menü öğesi tablosuna referans
    # quantity: Sipariş miktarı
    # total_price: Toplam fiyat
    # order_date: Sipariş tarihi
    # status: Sipariş durumu (pending, completed)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            item_id INTEGER,
            quantity INTEGER,
            total_price REAL,
            order_date TEXT,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (item_id) REFERENCES menu_items(id)
        )
    ''')
    
    # Çalışanlar tablosunu oluştur
    # user_id: Kullanıcı tablosuna referans
    # name: Çalışan adı
    # position: Pozisyon (Şef, Garson, vb.)
    # salary: Maaş bilgisi
    # email: E-posta adresi (benzersiz)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            salary REAL,
            email TEXT UNIQUE NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Eğer tablolar boşsa örnek veriler ekle
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        # Örnek kullanıcılar ekle
        users_data = [
            ('admin', 'admin123', 'admin', 'Sistem Yöneticisi'),
            ('ahmet', 'ahmet123', 'customer', 'Ahmet Yılmaz'),
            ('ayse', 'ayse123', 'customer', 'Ayşe Demir'),
            ('chef', 'chef123', 'employee', 'Ali Veli'),
        ]
        cursor.executemany('INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)', users_data)
        
        # Örnek menü öğeleri ekle
        menu_data = [
            ('Margherita Pizza', 'Pizza', 85.00, 'Domates, mozzarella, fesleğen ile hazırlanmış nefis pizza', '🍕'),
            ('Pepperoni Pizza', 'Pizza', 95.00, 'Domates, mozzarella, pepperoni ile lezzetli pizza', '🍕'),
            ('Spaghetti Carbonara', 'Pasta', 75.00, 'Makarna, yumurta, peynir, pastırma ile İtalyan klasik', '🍝'),
            ('Fettuccine Alfredo', 'Pasta', 70.00, 'Makarna, krema, parmesan peyniri', '🍝'),
            ('Caesar Salad', 'Salata', 45.00, 'Marul, parmesan, kruton, caesar sos', '🥗'),
            ('Greek Salad', 'Salata', 50.00, 'Domates, salatalık, zeytin, beyaz peynir', '🥗'),
            ('Grilled Salmon', 'Ana Yemek', 120.00, 'Izgara somon, sebze, pilav', '🐟'),
            ('Beef Steak', 'Ana Yemek', 150.00, 'Dana eti, patates, sebze', '🥩'),
            ('Tiramisu', 'Tatlı', 40.00, 'Kahveli İtalyan tatlısı', '🍰'),
            ('Chocolate Cake', 'Tatlı', 35.00, 'Çikolatalı pasta', '🎂'),
        ]
        cursor.executemany('INSERT INTO menu_items (name, category, price, description, image_url) VALUES (?, ?, ?, ?, ?)', menu_data)
        
        # Örnek müşteriler ekle
        customers_data = [
            (2, 'Ahmet Yılmaz', 'ahmet@example.com', '05551234567', 'İstanbul, Kadıköy'),
            (3, 'Ayşe Demir', 'ayse@example.com', '05559876543', 'Ankara, Çankaya'),
        ]
        cursor.executemany('INSERT INTO customers (user_id, name, email, phone, address) VALUES (?, ?, ?, ?, ?)', customers_data)
        
        # Örnek çalışanlar ekle
        employees_data = [
            (4, 'Ali Veli', 'Şef', 15000.00, 'ali.veli@restaurant.com'),
        ]
        cursor.executemany('INSERT INTO employees (user_id, name, position, salary, email) VALUES (?, ?, ?, ?, ?)', employees_data)
        
        # Örnek siparişler ekle
        orders_data = [
            (1, 1, 2, 170.00, '2025-01-15', 'completed'),
            (1, 3, 1, 75.00, '2025-01-16', 'completed'),
            (2, 7, 1, 120.00, '2025-01-17', 'pending'),
        ]
        cursor.executemany('INSERT INTO orders (customer_id, item_id, quantity, total_price, order_date, status) VALUES (?, ?, ?, ?, ?, ?)', orders_data)
        
        # Değişiklikleri veritabanına kaydet
        conn.commit()
        print("[+] Veritabanı örnek verilerle başlatıldı")
        print("    - Kullanıcılar: 4")
        print("    - Menü öğeleri: 10")
        print("    - Müşteriler: 2")
        print("    - Çalışanlar: 1")
        print("    - Siparişler: 3")
    
    # Veritabanı bağlantısını kapat
    conn.close()

def log_query(user_input, executed_query):
    """
    Kullanıcı girdisini ve çalıştırılan SQL sorgusunu terminale yazdırır.
    Bu fonksiyon, SQL Injection saldırılarını analiz etmek için kullanılır.
    
    Parametreler:
    - user_input: Kullanıcının girdiği veri
    - executed_query: Veritabanında çalıştırılan SQL sorgusu
    """
    # Zaman damgası oluştur
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{timestamp}]")
    print(f"[!] Kullanıcı Girdisi: {user_input}")
    print(f"[!] Çalıştırılan SQL Sorgusu: {executed_query}")
    print("-" * 70)

@app.route('/')
def index():
    """
    Ana sayfa (Login sayfası).
    Eğer kullanıcı zaten giriş yapmışsa menü sayfasına yönlendirir.
    """
    # Kullanıcı zaten giriş yapmışsa menüye yönlendir
    if session.get('logged_in'):
        return redirect(url_for('menu'))
    # Giriş yapmamışsa login sayfasını göster
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    """
    Kullanıcı giriş işlemini gerçekleştirir.
    
    GÜVENSİZ KOD: Bu fonksiyon SQL Injection açığı içerir!
    Kullanıcı girdisi doğrudan SQL sorgusuna ekleniyor.
    
    SQL Injection Payload Örneği:
    Kullanıcı Adı: ' OR '1'='1' --
    Şifre: (boş)
    """
    # Form'dan kullanıcı adı ve şifreyi al
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip() or ''  # Şifre boş olabilir
    
    # Kullanıcı adı kontrolü
    if not username:
        flash('Lütfen kullanıcı adı girin', 'error')
        return redirect(url_for('index'))
    
    # ⚠️ GÜVENSİZ KOD: String interpolation ile SQL sorgusu oluşturma
    # Kullanıcı girdisi doğrudan sorguya ekleniyor - SQL Injection açığı!
    # Bu kasıtlı olarak güvensiz bırakılmıştır (eğitim amaçlı)
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    
    # Sorguyu terminale yazdır (analiz için)
    log_query(f"username={username}, password={password}", query)
    
    try:
        # Veritabanı bağlantısını oluştur
        conn = sqlite3.connect(DB_FILE)
        # Satırları dictionary olarak döndür (kolay erişim için)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # ⚠️ GÜVENSİZ: Sorguyu doğrudan çalıştır (SQL Injection açığı burada!)
        cursor.execute(query)
        user = cursor.fetchone()
        
        # Veritabanı bağlantısını kapat
        conn.close()
        
        # Kullanıcı bulundu mu kontrol et
        if user:
            # Başarılı giriş - session bilgilerini kaydet
            session['logged_in'] = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['full_name'] = user['full_name']
            
            # Başarı mesajı göster ve menüye yönlendir
            flash(f'✅ Hoş geldiniz, {user["full_name"]}!', 'success')
            return redirect(url_for('menu'))
        else:
            # Kullanıcı bulunamadı - hata mesajı göster
            flash('❌ Kullanıcı adı veya şifre hatalı', 'error')
            return redirect(url_for('index'))
            
    except sqlite3.Error as e:
        # Veritabanı hatası durumunda hata mesajı göster
        flash(f'Veritabanı hatası: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """
    Kullanıcı çıkış işlemini gerçekleştirir.
    Tüm session bilgilerini temizler ve login sayfasına yönlendirir.
    """
    # Tüm session verilerini temizle
    session.clear()
    flash('Başarıyla çıkış yapıldı', 'info')
    return redirect(url_for('index'))

@app.route('/menu')
def menu():
    """
    Menü sayfasını gösterir.
    Giriş yapmış kullanıcılar için menü öğelerini kategorilere göre listeler.
    """
    # Giriş kontrolü - giriş yapmamışsa login sayfasına yönlendir
    if not session.get('logged_in'):
        flash('Lütfen önce giriş yapın', 'error')
        return redirect(url_for('index'))
    
    try:
        # Veritabanı bağlantısını oluştur
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Tüm menü öğelerini kategori ve isme göre sıralayarak getir
        cursor.execute("SELECT * FROM menu_items ORDER BY category, name")
        menu_items = [dict(row) for row in cursor.fetchall()]
        
        # Menü öğelerini kategorilere göre grupla
        menu_by_category = {}
        for item in menu_items:
            category = item['category']
            # Eğer kategori henüz yoksa oluştur
            if category not in menu_by_category:
                menu_by_category[category] = []
            # Öğeyi ilgili kategoriye ekle
            menu_by_category[category].append(item)
        
        # Veritabanı bağlantısını kapat
        conn.close()
        
        # Menü sayfasını render et
        return render_template('menu.html', 
                             menu_by_category=menu_by_category,
                             user=session)
    except sqlite3.Error as e:
        # Veritabanı hatası durumunda hata mesajı göster
        flash(f'Veritabanı hatası: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/search', methods=['POST'])
def search():
    """
    Menü arama fonksiyonu.
    Kullanıcının girdiği terime göre menü öğelerini arar.
    
    GÜVENLİ KOD: Parametreli sorgular kullanılıyor.
    """
    # Giriş kontrolü
    if not session.get('logged_in'):
        flash('Lütfen önce giriş yapın', 'error')
        return redirect(url_for('index'))
    
    # Form'dan arama terimini al
    search_term = request.form.get('search', '').strip()
    
    # Arama terimi kontrolü
    if not search_term:
        flash('Lütfen bir arama terimi girin', 'error')
        return redirect(url_for('menu'))
    
    # ✓ GÜVENLİ KOD: Parametreli sorgu kullanılıyor
    # SQL Injection açığı yok - kullanıcı girdisi parametre olarak geçiriliyor
    query_template = "SELECT * FROM menu_items WHERE name LIKE ? OR description LIKE ?"
    search_pattern = f'%{search_term}%'  # LIKE için pattern oluştur
    
    # Sorguyu terminale yazdır (analiz için)
    log_query(search_term, f"SELECT * FROM menu_items WHERE name LIKE '%{search_term}%' OR description LIKE '%{search_term}%' (parameterized)")
    
    try:
        # Veritabanı bağlantısını oluştur
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # ✓ GÜVENLİ: Parametreli sorguyu çalıştır
        cursor.execute(query_template, (search_pattern, search_pattern))
        results = cursor.fetchall()
        menu_items = [dict(row) for row in results]
        
        # Veritabanı bağlantısını kapat
        conn.close()
        
        # Sonuç mesajı göster
        if menu_items:
            flash(f'{len(menu_items)} sonuç bulundu', 'success')
        else:
            flash('Sonuç bulunamadı', 'info')
        
        # Arama sonuçları sayfasını render et
        return render_template('search_results.html', 
                             menu_items=menu_items,
                             search_term=search_term,
                             executed_query=query_template,
                             user=session)
            
    except sqlite3.Error as e:
        # Veritabanı hatası durumunda hata mesajı göster
        flash(f'Veritabanı hatası: {str(e)}', 'error')
        return redirect(url_for('menu'))

@app.route('/database')
def show_database():
    """
    Veritabanı yönetim sayfası.
    Tüm tabloları ve verilerini gösterir. Admin paneli içerir.
    """
    # Giriş kontrolü
    if not session.get('logged_in'):
        flash('Lütfen önce giriş yapın', 'error')
        return redirect(url_for('index'))
    
    try:
        # Veritabanı bağlantısını oluştur
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Tüm tablo isimlerini getir
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Her tablodaki verileri getir
        db_data = {}
        for table in tables:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            db_data[table] = [dict(row) for row in rows]
        
        # Veritabanı bağlantısını kapat
        conn.close()
        
        # Kullanıcının admin olup olmadığını kontrol et
        is_admin = session.get('role') == 'admin'
        
        # Veritabanı sayfasını render et
        return render_template('database.html', db_data=db_data, tables=tables, user=session, is_admin=is_admin)
    except sqlite3.Error as e:
        # Veritabanı hatası durumunda hata mesajı göster
        flash(f'Veritabanı hatası: {str(e)}', 'error')
        return redirect(url_for('menu'))

@app.route('/admin/add_user', methods=['POST'])
def add_user():
    """
    Yeni kullanıcı ekleme fonksiyonu (sadece admin).
    
    GÜVENLİ KOD: Parametreli sorgular kullanılıyor.
    """
    # Giriş kontrolü
    if not session.get('logged_in'):
        flash('Lütfen önce giriş yapın', 'error')
        return redirect(url_for('index'))
    
    # Admin yetkisi kontrolü
    if session.get('role') != 'admin':
        flash('Bu işlem için admin yetkisi gereklidir', 'error')
        return redirect(url_for('show_database'))
    
    # Form'dan kullanıcı bilgilerini al
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    full_name = request.form.get('full_name', '').strip()
    role = request.form.get('role', 'customer').strip()
    
    # Zorunlu alan kontrolü
    if not username or not password:
        flash('Kullanıcı adı ve şifre gereklidir', 'error')
        return redirect(url_for('show_database'))
    
    # ✓ GÜVENLİ KOD: Parametreli sorgu kullanılıyor
    query_template = "INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)"
    
    # Sorguyu terminale yazdır
    log_query(f"username={username}, password={password}, role={role}, full_name={full_name}", 
              f"INSERT INTO users (username, password, role, full_name) VALUES ('{username}', '{password}', '{role}', '{full_name}') (parameterized)")
    
    try:
        # Veritabanı bağlantısını oluştur
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # ✓ GÜVENLİ: Parametreli sorguyu çalıştır
        cursor.execute(query_template, (username, password, role, full_name))
        conn.commit()
        conn.close()
        
        # Başarı mesajı göster
        flash(f'✅ Kullanıcı başarıyla eklendi: {username}', 'success')
    except sqlite3.IntegrityError:
        # Kullanıcı adı zaten kullanılıyorsa hata mesajı göster
        flash('❌ Bu kullanıcı adı zaten kullanılıyor', 'error')
    except sqlite3.Error as e:
        # Diğer veritabanı hataları için hata mesajı göster
        flash(f'Veritabanı hatası: {str(e)}', 'error')
    
    # Veritabanı sayfasına geri dön
    return redirect(url_for('show_database'))

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """
    Kullanıcı silme fonksiyonu (sadece admin).
    
    GÜVENLİ KOD: Parametreli sorgular kullanılıyor.
    """
    # Giriş ve admin yetkisi kontrolü
    if not session.get('logged_in') or session.get('role') != 'admin':
        flash('Bu işlem için admin yetkisi gereklidir', 'error')
        return redirect(url_for('show_database'))
    
    # ✓ GÜVENLİ KOD: Parametreli sorgu kullanılıyor
    query_template = "DELETE FROM users WHERE id = ?"
    
    # Sorguyu terminale yazdır
    log_query(f"user_id={user_id}", f"DELETE FROM users WHERE id = {user_id} (parameterized)")
    
    try:
        # Veritabanı bağlantısını oluştur
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # ✓ GÜVENLİ: Parametreli sorguyu çalıştır
        cursor.execute(query_template, (user_id,))
        conn.commit()
        conn.close()
        
        # Başarı mesajı göster
        flash('✅ Kullanıcı başarıyla silindi', 'success')
    except sqlite3.Error as e:
        # Veritabanı hatası durumunda hata mesajı göster
        flash(f'Veritabanı hatası: {str(e)}', 'error')
    
    # Veritabanı sayfasına geri dön
    return redirect(url_for('show_database'))

@app.route('/reset', methods=['POST'])
def reset():
    """
    Veritabanını sıfırlar ve başlangıç durumuna getirir.
    Mevcut veritabanı dosyasını siler ve yeniden oluşturur.
    """
    # Eğer veritabanı dosyası varsa sil
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    # Veritabanını yeniden başlat
    init_database()
    flash('Veritabanı başarıyla sıfırlandı', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Uygulama başlatıldığında çalışacak kod
    print("\n" + "=" * 70)
    print("🍕 Restoran Menü Sistemi - SQL Injection Demo")
    print("=" * 70)
    print("\n⚠️  UYARI: Bu uygulama kasıtlı güvenlik açıkları içerir!")
    print("   Sadece eğitim amaçlıdır.\n")
    
    # Veritabanını başlat
    init_database()
    
    # Sunucu başlatma mesajları
    print("\n[+] Flask sunucusu başlatılıyor...")
    print("[+] Tarayıcınızdan şu adrese gidin: http://127.0.0.1:5000")
    print("[+] Sunucuyu durdurmak için CTRL+C tuşlarına basın\n")
    print("=" * 70 + "\n")
    
    # Flask sunucusunu başlat
    app.run(debug=True, host='127.0.0.1', port=5000)
