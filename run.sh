#!/bin/bash
# Healthcare Assistant - Run with Live Logs in Terminal

echo "🏥 Healthcare Assistant - Interactive Mode"
echo "==========================================="
echo ""
echo "Starting server with live logs..."
echo "You'll see all API calls and tool executions here!"
echo ""
echo "📍 Backend: http://localhost:8000"
echo "📱 Frontend: Open frontend/index.html in your browser"
echo ""
echo "⏹️  Press Ctrl+C to stop"
echo "==========================================="
echo ""

# Activate virtual environment
source .venv/bin/activate

# Run server directly (logs will show in terminal)
python main.py
