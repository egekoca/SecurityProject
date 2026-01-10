"""
SQL Injection Vulnerability Demo Application
This application demonstrates SQL Injection vulnerabilities for educational purposes.
WARNING: This code contains intentional security vulnerabilities. DO NOT use in production!
"""

from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'demo_secret_key_change_in_production'

# Database file path
DB_FILE = 'users.db'

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
    print("-" * 60)

@app.route('/')
def index():
    """Main login page"""
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """Login handler with SQL Injection vulnerability"""
    username = request.form.get('username', '').strip()
    
    if not username:
        flash('Please enter a username', 'error')
        return redirect(url_for('index'))
    
    # VULNERABLE CODE: Direct string interpolation (SQL Injection vulnerability)
    # This is intentionally insecure for educational purposes
    query = f"SELECT * FROM users WHERE username = '{username}'"
    
    # Log the query to terminal
    log_query(username, query)
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Execute the vulnerable query
        cursor.execute(query)
        user = cursor.fetchone()
        
        conn.close()
        
        if user:
            # Success - user found
            flash(f'✅ SUCCESS! Welcome {user[1]}', 'success')
            return render_template('result.html', 
                                 username=user[1], 
                                 user_input=username,
                                 executed_query=query,
                                 success=True)
        else:
            # User not found
            flash('❌ ERROR: User not found', 'error')
            return render_template('result.html',
                                 username=None,
                                 user_input=username,
                                 executed_query=query,
                                 success=False)
            
    except sqlite3.Error as e:
        flash(f'Database error: {str(e)}', 'error')
        return render_template('result.html',
                             username=None,
                             user_input=username,
                             executed_query=query,
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
    print("🛡️  SQL Injection Vulnerability Demo")
    print("=" * 60)
    print("\n⚠️  WARNING: This application contains intentional security vulnerabilities!")
    print("   This is for educational purposes only.\n")
    
    # Initialize database
    init_database()
    
    print("\n[+] Starting Flask server...")
    print("[+] Open your browser and navigate to: http://127.0.0.1:5000")
    print("[+] Press CTRL+C to stop the server\n")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)

