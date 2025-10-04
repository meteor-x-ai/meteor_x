import sys
import subprocess
import threading
import sys
from pathlib import Path

#start main program
main_path = Path(__file__).parent / "this" / "is" / "way"
subprocess.run([sys.executable, str(main_path)])
BASE_DIR = Path(__file__).parent
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"

def run_backend():
    subprocess.run([sys.executable, "app.py"], cwd=str(BACKEND_DIR))

def run_frontend():
    subprocess.run(["npm", "run", "dev"], cwd=str(FRONTEND_DIR))

if __name__ == "__main__":
    frontend_thread = threading.Thread(target=run_frontend)
    frontend_thread.daemon = True
    frontend_thread.start()

    run_backend()