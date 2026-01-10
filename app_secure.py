"""
Secure Version - SQL Injection Protection
This version uses parameterized queries to prevent SQL Injection attacks.
"""

from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'demo_secret_key_change_in_production'

# Database file path
DB_FILE = 'users_secure.db'

def init_database():
    """Initialize the database with sample users"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Insert sample users (only if table is empty)
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin123')")
        cursor.execute("INSERT INTO users (username, password) VALUES ('user1', 'password1')")
        cursor.execute("INSERT INTO users (username, password) VALUES ('test', 'test123')")
        conn.commit()
        print("[+] Database initialized with sample users")
    
    conn.close()

def log_query(user_input, executed_query):
    """Log user input and executed SQL query to terminal"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{timestamp}]")
    print(f"[!] User Input: {user_input}")
    print(f"[!] Executed SQL Query: {executed_query}")
    print(f"[✓] Using Parameterized Query (SAFE)")
    print("-" * 60)

@app.route('/')
def index():
    """Main login page"""
    return render_template('index_secure.html')

@app.route('/login', methods=['POST'])
def login():
    """Login handler with SQL Injection protection"""
    username = request.form.get('username', '').strip()
    
    if not username:
        flash('Please enter a username', 'error')
        return redirect(url_for('index'))
    
    # SECURE CODE: Parameterized query (prevents SQL Injection)
    query_template = "SELECT * FROM users WHERE username = ?"
    
    # Log the query to terminal
    log_query(username, f"SELECT * FROM users WHERE username = '{username}' (parameterized)")
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Execute the secure parameterized query
        # The username is passed as a parameter, not concatenated into the query
        cursor.execute(query_template, (username,))
        user = cursor.fetchone()
        
        conn.close()
        
        if user:
            # Success - user found
            flash(f'✅ SUCCESS! Welcome {user[1]}', 'success')
            return render_template('result_secure.html', 
                                 username=user[1], 
                                 user_input=username,
                                 executed_query=query_template,
                                 success=True)
        else:
            # User not found
            flash('❌ ERROR: User not found', 'error')
            return render_template('result_secure.html',
                                 username=None,
                                 user_input=username,
                                 executed_query=query_template,
                                 success=False)
            
    except sqlite3.Error as e:
        flash(f'Database error: {str(e)}', 'error')
        return render_template('result_secure.html',
                             username=None,
                             user_input=username,
                             executed_query=query_template,
                             success=False)

@app.route('/reset', methods=['POST'])
def reset():
    """Reset database to initial state"""
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    init_database()
    flash('Database reset successfully', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🛡️  SQL Injection Protection Demo (SECURE VERSION)")
    print("=" * 60)
    print("\n✓ This version uses parameterized queries to prevent SQL Injection.\n")
    
    # Initialize database
    init_database()
    
    print("\n[+] Starting Flask server...")
    print("[+] Open your browser and navigate to: http://127.0.0.1:5001")
    print("[+] Press CTRL+C to stop the server\n")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5001)

