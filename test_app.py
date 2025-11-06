import sys
import os

# Add ecopulse to path
sys.path.append('ecopulse')

try:
    from ecopulse.app.main import app
    print("✅ SUCCESS: App imported correctly!")
    print("✅ App title:", app.title)
except Exception as e:
    print("❌ ERROR:", e)
    print("Current directory:", os.getcwd())
    print("Files in current directory:", os.listdir('.'))
    if os.path.exists('ecopulse'):
        print("Files in ecopulse:", os.listdir('ecopulse'))
        if os.path.exists('ecopulse/app'):
            print("Files in ecopulse/app:", os.listdir('ecopulse/app'))