#!/bin/bash

# SQL Injection Demo - Run Script
echo "🛡️  Starting SQL Injection Demo..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run the application
python3 app.py
