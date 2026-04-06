#!/bin/bash
# Healthcare Assistant - Quick Start Script

echo "🏥 Healthcare Assistant - Quick Start"
echo "======================================"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies if needed
if [ ! -f ".venv/installed" ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    touch .venv/installed
fi

# Start the server
echo ""
echo "🚀 Starting Healthcare Assistant Server..."
echo "📍 Backend: http://localhost:8000"
echo "📱 Frontend: Open frontend/index.html in your browser"
echo ""
echo "⏹️  Press Ctrl+C to stop"
echo "======================================"
echo ""

python main.py
