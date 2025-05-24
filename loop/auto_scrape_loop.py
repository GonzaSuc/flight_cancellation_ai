import time
import subprocess
from datetime import datetime

def loop_scraping(interval_minutes=30):
    print(f"🕒 Iniciando recolección automática cada {interval_minutes} minutos...")

    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n🗓️ {timestamp} - Ejecutando scrape_corpac_post.py")
        subprocess.run(["python", "scripts/scrape_corpac_post.py"])

        print(f"🕑 Esperando {interval_minutes} minutos antes del siguiente ciclo...\n")
        time.sleep(interval_minutes * 60)

if __name__ == "__main__":
    loop_scraping(interval_minutes=30)  # Puedes cambiar a 60 o 15
