"""
Database initialization script
Creates the database and populates it with sample users
"""

import sqlite3
import os

DB_FILE = 'users.db'

def init_database():
    """Initialize the database with sample users"""
    # Remove existing database if it exists
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"[+] Removed existing database: {DB_FILE}")
    
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
    
    # Insert sample users
    users = [
        ('admin', 'admin123'),
        ('user1', 'password1'),
        ('test', 'test123')
    ]
    
    for username, password in users:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    
    conn.commit()
    conn.close()
    
    print(f"[+] Database created: {DB_FILE}")
    print(f"[+] Inserted {len(users)} sample users")
    print("\nSample users:")
    for username, password in users:
        print(f"  - Username: {username}, Password: {password}")

if __name__ == '__main__':
    print("=" * 60)
    print("Database Initialization")
    print("=" * 60 + "\n")
    init_database()
    print("\n[+] Database initialization completed!")

