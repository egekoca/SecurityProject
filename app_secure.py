"""
Restoran Menü Sistemi - Güvenli Versiyon
Bu versiyon parametreli sorgular kullanarak SQL Injection saldırılarını önler.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'demo_secret_key_change_in_production'

# Database file path
DB_FILE = 'restaurant_secure.db'

def init_database():
    """Initialize the database with restaurant data"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'customer',
            full_name TEXT
        )
    ''')
    
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
    
    # Insert sample data
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        users_data = [
            ('admin', 'admin123', 'admin', 'Sistem Yöneticisi'),
            ('ahmet', 'ahmet123', 'customer', 'Ahmet Yılmaz'),
            ('ayse', 'ayse123', 'customer', 'Ayşe Demir'),
            ('chef', 'chef123', 'employee', 'Ali Veli'),
        ]
        cursor.executemany('INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)', users_data)
        
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
        
        customers_data = [
            (2, 'Ahmet Yılmaz', 'ahmet@example.com', '05551234567', 'İstanbul, Kadıköy'),
            (3, 'Ayşe Demir', 'ayse@example.com', '05559876543', 'Ankara, Çankaya'),
        ]
        cursor.executemany('INSERT INTO customers (user_id, name, email, phone, address) VALUES (?, ?, ?, ?, ?)', customers_data)
        
        employees_data = [
            (4, 'Ali Veli', 'Şef', 15000.00, 'ali.veli@restaurant.com'),
        ]
        cursor.executemany('INSERT INTO employees (user_id, name, position, salary, email) VALUES (?, ?, ?, ?, ?)', employees_data)
        
        orders_data = [
            (1, 1, 2, 170.00, '2025-01-15', 'completed'),
            (1, 3, 1, 75.00, '2025-01-16', 'completed'),
            (2, 7, 1, 120.00, '2025-01-17', 'pending'),
        ]
        cursor.executemany('INSERT INTO orders (customer_id, item_id, quantity, total_price, order_date, status) VALUES (?, ?, ?, ?, ?, ?)', orders_data)
        
        conn.commit()
        print("[+] Veritabanı örnek verilerle başlatıldı")
    
    conn.close()

def log_query(user_input, executed_query):
    """Log user input and executed SQL query to terminal"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{timestamp}]")
    print(f"[!] Kullanıcı Girdisi: {user_input}")
    print(f"[!] Çalıştırılan SQL Sorgusu: {executed_query}")
    print(f"[✓] Parametreli Sorgu Kullanılıyor (GÜVENLİ)")
    print("-" * 70)

@app.route('/')
def index():
    """Login page"""
    if session.get('logged_in'):
        return redirect(url_for('menu'))
    return render_template('login_secure.html')

@app.route('/login', methods=['POST'])
def login():
    """Login handler with SQL Injection protection"""
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    
    if not username:
        flash('Lütfen kullanıcı adı girin', 'error')
        return redirect(url_for('index'))
    
    # SECURE CODE: Parameterized query
    query_template = "SELECT * FROM users WHERE username = ? AND password = ?"
    
    log_query(f"username={username}, password={password}", f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}' (parameterized)")
    
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(query_template, (username, password))
        user = cursor.fetchone()
        
        conn.close()
        
        if user:
            session['logged_in'] = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['full_name'] = user['full_name']
            
            flash(f'✅ Hoş geldiniz, {user["full_name"]}!', 'success')
            return redirect(url_for('menu'))
        else:
            flash('❌ Kullanıcı adı veya şifre hatalı', 'error')
            return redirect(url_for('index'))
            
    except sqlite3.Error as e:
        flash(f'Veritabanı hatası: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """Logout handler"""
    session.clear()
    flash('Başarıyla çıkış yapıldı', 'info')
    return redirect(url_for('index'))

@app.route('/menu')
def menu():
    """Menu page - requires login"""
    if not session.get('logged_in'):
        flash('Lütfen önce giriş yapın', 'error')
        return redirect(url_for('index'))
    
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM menu_items ORDER BY category, name")
        menu_items = [dict(row) for row in cursor.fetchall()]
        
        menu_by_category = {}
        for item in menu_items:
            category = item['category']
            if category not in menu_by_category:
                menu_by_category[category] = []
            menu_by_category[category].append(item)
        
        conn.close()
        
        return render_template('menu_secure.html', 
                             menu_by_category=menu_by_category,
                             user=session)
    except sqlite3.Error as e:
        flash(f'Veritabanı hatası: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/search', methods=['POST'])
def search():
    """Menu search with SQL Injection protection"""
    if not session.get('logged_in'):
        flash('Lütfen önce giriş yapın', 'error')
        return redirect(url_for('index'))
    
    search_term = request.form.get('search', '').strip()
    
    if not search_term:
        flash('Lütfen bir arama terimi girin', 'error')
        return redirect(url_for('menu'))
    
    # SECURE CODE: Parameterized query
    query_template = "SELECT * FROM menu_items WHERE name LIKE ? OR description LIKE ?"
    search_pattern = f'%{search_term}%'
    
    log_query(search_term, f"SELECT * FROM menu_items WHERE name LIKE '%{search_term}%' OR description LIKE '%{search_term}%' (parameterized)")
    
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(query_template, (search_pattern, search_pattern))
        results = cursor.fetchall()
        menu_items = [dict(row) for row in results]
        
        conn.close()
        
        if menu_items:
            flash(f'{len(menu_items)} sonuç bulundu', 'success')
        else:
            flash('Sonuç bulunamadı', 'info')
        
        return render_template('search_results_secure.html', 
                             menu_items=menu_items,
                             search_term=search_term,
                             executed_query=query_template,
                             user=session)
            
    except sqlite3.Error as e:
        flash(f'Veritabanı hatası: {str(e)}', 'error')
        return redirect(url_for('menu'))

@app.route('/database')
def show_database():
    """Show all database tables"""
    if not session.get('logged_in'):
        flash('Lütfen önce giriş yapın', 'error')
        return redirect(url_for('index'))
    
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        db_data = {}
        for table in tables:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            db_data[table] = [dict(row) for row in rows]
        
        conn.close()
        
        return render_template('database_secure.html', db_data=db_data, tables=tables, user=session)
    except sqlite3.Error as e:
        flash(f'Veritabanı hatası: {str(e)}', 'error')
        return redirect(url_for('menu'))

@app.route('/reset', methods=['POST'])
def reset():
    """Reset database"""
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    init_database()
    flash('Veritabanı başarıyla sıfırlandı', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("🍕 Restoran Menü Sistemi - Güvenli Versiyon")
    print("=" * 70)
    print("\n✓ Bu versiyon parametreli sorgular kullanarak SQL Injection'ı önler.\n")
    
    init_database()
    
    print("\n[+] Flask sunucusu başlatılıyor...")
    print("[+] Tarayıcınızdan şu adrese gidin: http://127.0.0.1:5001")
    print("[+] Sunucuyu durdurmak için CTRL+C tuşlarına basın\n")
    print("=" * 70 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5001)
