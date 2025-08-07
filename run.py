import subprocess
import sys
import time
import threading

def run_flask():
    """Run the Flask application"""
    subprocess.run([sys.executable, 'app.py'])

def run_vite():
    """Run the Vite development server"""
    time.sleep(2)  # Wait for Flask to start
    subprocess.run(['npm', 'run', 'dev'])

if __name__ == '__main__':
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Start Vite (this will block)
    run_vite()
