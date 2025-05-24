# scripts/auto_fetch_openmeteo_loop.py

import time
import subprocess
from datetime import datetime

def loop_openmeteo(interval_min=60):
    print(f"🌍 Iniciando recolección automática de Open-Meteo cada {interval_min} minutos...")

    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n🗓️ {timestamp} - Ejecutando fetch_openmeteo_multi.py")
        subprocess.run(["python", "scripts/fetch_openmeteo_multi.py"])

        print(f"🕒 Esperando {interval_min} minutos...\n")
        time.sleep(interval_min * 60)

if __name__ == "__main__":
    loop_openmeteo(interval_min=60)
