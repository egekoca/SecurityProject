#!/bin/bash

# SQL Injection Demo - Setup Script
echo "🛡️  SQL Injection Demo - Setting up environment..."
echo ""

# Create virtual environment
echo "[1/3] Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "[2/3] Activating virtual environment..."
source venv/bin/activate

# Install Flask
echo "[3/3] Installing Flask..."
pip install flask

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the application:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run the app: python3 app.py"
echo ""
echo "Or use the run script: ./run.sh"
