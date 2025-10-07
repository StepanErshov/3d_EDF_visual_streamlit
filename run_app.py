"""
Launch script for the Advanced Medical Visualization Tool
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required packages"""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if requirements_file.exists():
        print("📦 Installing required packages...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
            print("✅ Requirements installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing requirements: {e}")
            return False
    else:
        print("⚠️ requirements.txt not found")
        return False

def run_streamlit_app():
    """Run the Streamlit application"""
    app_file = Path(__file__).parent / "app.py"
    
    if app_file.exists():
        print("🚀 Starting Advanced Medical Visualization Tool...")
        print("📱 The application will open in your default web browser")
        print("🔗 If it doesn't open automatically, navigate to: http://localhost:8501")
        print("⏹️  Press Ctrl+C to stop the application")
        print("-" * 60)
        
        try:
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", str(app_file),
                "--server.port", "8501",
                "--server.address", "localhost",
                "--browser.gatherUsageStats", "false"
            ])
        except KeyboardInterrupt:
            print("\n👋 Application stopped by user")
        except Exception as e:
            print(f"❌ Error running application: {e}")
    else:
        print("❌ app.py not found")

def main():
    """Main function"""
    print("🧠 Advanced Medical Visualization Tool")
    print("=" * 50)
    
    # Проверяем, установлены ли зависимости
    try:
        import streamlit
        import numpy
        import nibabel
        import plotly
        print("✅ All required packages are available")
    except ImportError as e:
        print(f"⚠️ Missing package: {e}")
        install_choice = input("Do you want to install missing packages? (y/n): ").lower()
        if install_choice == 'y':
            if not install_requirements():
                print("❌ Failed to install requirements. Please install manually.")
                return
        else:
            print("❌ Cannot run application without required packages")
            return
    
    # Запускаем приложение
    run_streamlit_app()

if __name__ == "__main__":
    main()
