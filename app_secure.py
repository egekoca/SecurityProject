"""
Restoran Menü Sistemi - Güvenli Versiyon
Bu versiyon parametreli sorgular kullanarak SQL Injection saldırılarını önler.
"""

from flask import Flask, render_template, request, redirect, url_for, flash
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
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            address TEXT
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
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (item_id) REFERENCES menu_items(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            salary REAL,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Insert sample data (only if tables are empty)
    cursor.execute('SELECT COUNT(*) FROM menu_items')
    if cursor.fetchone()[0] == 0:
        # Menu items
        menu_data = [
            ('Margherita Pizza', 'Pizza', 85.00, 'Domates, mozzarella, fesleğen'),
            ('Pepperoni Pizza', 'Pizza', 95.00, 'Domates, mozzarella, pepperoni'),
            ('Spaghetti Carbonara', 'Pasta', 75.00, 'Makarna, yumurta, peynir, pastırma'),
            ('Fettuccine Alfredo', 'Pasta', 70.00, 'Makarna, krema, parmesan'),
            ('Caesar Salad', 'Salata', 45.00, 'Marul, parmesan, kruton, caesar sos'),
            ('Greek Salad', 'Salata', 50.00, 'Domates, salatalık, zeytin, peynir'),
            ('Grilled Salmon', 'Ana Yemek', 120.00, 'Izgara somon, sebze, pilav'),
            ('Beef Steak', 'Ana Yemek', 150.00, 'Dana eti, patates, sebze'),
            ('Tiramisu', 'Tatlı', 40.00, 'Kahveli İtalyan tatlısı'),
            ('Chocolate Cake', 'Tatlı', 35.00, 'Çikolatalı pasta'),
        ]
        cursor.executemany('INSERT INTO menu_items (name, category, price, description) VALUES (?, ?, ?, ?)', menu_data)
        
        # Customers
        customers_data = [
            ('Ahmet Yılmaz', 'ahmet@example.com', '05551234567', 'İstanbul, Kadıköy'),
            ('Ayşe Demir', 'ayse@example.com', '05559876543', 'Ankara, Çankaya'),
            ('Mehmet Kaya', 'mehmet@example.com', '05551112233', 'İzmir, Konak'),
            ('Fatma Şahin', 'fatma@example.com', '05554445566', 'Bursa, Nilüfer'),
        ]
        cursor.executemany('INSERT INTO customers (name, email, phone, address) VALUES (?, ?, ?, ?)', customers_data)
        
        # Employees
        employees_data = [
            ('Ali Veli', 'Şef', 15000.00, 'ali.veli@restaurant.com'),
            ('Zeynep Ak', 'Garson', 8000.00, 'zeynep.ak@restaurant.com'),
            ('Can Öz', 'Kasiyer', 7500.00, 'can.oz@restaurant.com'),
            ('Elif Yıldız', 'Müdür', 20000.00, 'elif.yildiz@restaurant.com'),
        ]
        cursor.executemany('INSERT INTO employees (name, position, salary, email) VALUES (?, ?, ?, ?)', employees_data)
        
        # Orders
        orders_data = [
            (1, 1, 2, 170.00, '2025-01-15'),
            (2, 3, 1, 75.00, '2025-01-16'),
            (1, 7, 1, 120.00, '2025-01-17'),
            (3, 2, 3, 285.00, '2025-01-18'),
        ]
        cursor.executemany('INSERT INTO orders (customer_id, item_id, quantity, total_price, order_date) VALUES (?, ?, ?, ?, ?)', orders_data)
        
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
    """Main menu search page"""
    return render_template('index_secure.html')

@app.route('/search', methods=['POST'])
def search():
    """Menu search with SQL Injection protection"""
    search_term = request.form.get('search', '').strip()
    
    if not search_term:
        flash('Lütfen bir arama terimi girin', 'error')
        return redirect(url_for('index'))
    
    # SECURE CODE: Parameterized query (prevents SQL Injection)
    query_template = "SELECT * FROM menu_items WHERE name LIKE ? OR description LIKE ?"
    search_pattern = f'%{search_term}%'
    
    # Log the query to terminal
    log_query(search_term, f"SELECT * FROM menu_items WHERE name LIKE '%{search_term}%' OR description LIKE '%{search_term}%' (parameterized)")
    
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Execute the secure parameterized query
        cursor.execute(query_template, (search_pattern, search_pattern))
        results = cursor.fetchall()
        
        # Convert rows to dictionaries
        menu_items = [dict(row) for row in results]
        
        conn.close()
        
        if menu_items:
            flash(f'{len(menu_items)} sonuç bulundu', 'success')
        else:
            flash('Sonuç bulunamadı', 'info')
        
        return render_template('results_secure.html', 
                             menu_items=menu_items,
                             search_term=search_term,
                             executed_query=query_template)
            
    except sqlite3.Error as e:
        flash(f'Veritabanı hatası: {str(e)}', 'error')
        return render_template('results_secure.html',
                             menu_items=[],
                             search_term=search_term,
                             executed_query=query_template,
                             error=str(e))

@app.route('/database')
def show_database():
    """Show all database tables (for demonstration)"""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Get data from each table
        db_data = {}
        for table in tables:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            db_data[table] = [dict(row) for row in rows]
        
        conn.close()
        
        return render_template('database_secure.html', db_data=db_data, tables=tables)
    except sqlite3.Error as e:
        flash(f'Veritabanı hatası: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/reset', methods=['POST'])
def reset():
    """Reset database to initial state"""
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
    
    # Initialize database
    init_database()
    
    print("\n[+] Flask sunucusu başlatılıyor...")
    print("[+] Tarayıcınızdan şu adrese gidin: http://127.0.0.1:5001")
    print("[+] Sunucuyu durdurmak için CTRL+C tuşlarına basın\n")
    print("=" * 70 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5001)
