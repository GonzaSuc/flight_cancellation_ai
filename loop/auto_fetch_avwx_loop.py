import time
import subprocess
from datetime import datetime

def loop_avwx(interval_min=10):
    print(f"🔁 Iniciando recolección de AVWX cada {interval_min} minutos...")

    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n🗓️ {timestamp} - Ejecutando fetch_avwx_multi.py")
        subprocess.run(["python", "scripts/fetch_avwx_multi.py"])

        print(f"🕒 Esperando {interval_min} minutos...")
        time.sleep(interval_min * 60)

if __name__ == "__main__":
    loop_avwx(interval_min=60)
