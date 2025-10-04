import subprocess
import threading
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"

def run_backend():
    subprocess.run([sys.executable, "app.py"], cwd=str(BACKEND_DIR))

def run_frontend():
    subprocess.run(["npm", "install"], cwd=str(FRONTEND_DIR))
    subprocess.run(["npm", "run", "dev"], cwd=str(FRONTEND_DIR))

if __name__ == "__main__":
    frontend_thread = threading.Thread(target=run_frontend)
    frontend_thread.daemon = True
    frontend_thread.start()

    run_backend()