# scripts/hourly_data_pipeline.py

import subprocess
import time
from datetime import datetime

def run_script(script_name):
    print(f"\n⏳ Ejecutando {script_name}...")
    try:
        subprocess.run(["python", f"scripts/{script_name}"], check=True)
        print(f"✅ Finalizado: {script_name}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando {script_name}: {e}")

def run_hourly_pipeline():
    while True:
        print(f"\n🕒 Iniciando ciclo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Paso 1: Recolección
        run_script("fetch_avwx_multi.py")
        run_script("scrape_corpac_post.py")
        run_script("fetch_openmeteo_multi.py")

        # Paso 2: Parser METAR
        run_script("parse_metar_csv.py")

        # Paso 3: Unificación
        run_script("merge_datasets.py")

        # Paso 4: Limpieza final
        run_script("clean_final_merged.py")

        # Paso 5: Evaluación de condiciones de vuelo
        run_script("check_flight_status.py")

        print(f"\n✅ Ciclo completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("⏳ Esperando 1 hora para el próximo ciclo...\n")
        time.sleep(3600)  # Esperar una hora

if __name__ == "__main__":
    run_hourly_pipeline()
