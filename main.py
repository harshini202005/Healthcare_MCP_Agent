#!/usr/bin/env python3
"""
Healthcare Assistant - Main Launcher
Run this file to start the backend server
"""

import sys
import os
import subprocess

def main():
    print("🏥 Healthcare Assistant - Starting Backend Server...")
    print("=" * 60)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Virtual environment not activated!")
        print("\n📝 To activate, run:")
        print("   source .venv/bin/activate")
        print("\nOr let me start it anyway...\n")
    
    # Get the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        print("🚀 Starting server on http://localhost:8000")
        print("📱 Open frontend/index.html in your browser")
        print("⏹️  Press Ctrl+C to stop the server")
        print("=" * 60)
        print()
        
        # Start uvicorn server
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "backend.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ], cwd=project_dir)
        
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped successfully!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("\n💡 Make sure you have installed dependencies:")
        print("   pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
