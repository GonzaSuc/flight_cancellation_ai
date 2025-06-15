# scripts/hourly_data_pipeline.py

import subprocess
import time
from datetime import datetime

def run_script(script_path):
    print(f"\n⏳ Ejecutando {script_path}...")
    try:
        subprocess.run(["python", script_path], check=True)
        print(f"✅ Finalizado: {script_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando {script_path}: {e}")

def run_hourly_pipeline():
    while True:
        print(f"\n🕒 Iniciando ciclo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Paso 1: Recolección
        run_script("scripts/fetch_avwx_multi.py")
        run_script("scripts/scrape_corpac_post.py")
        run_script("scripts/fetch_openmeteo_multi.py")

        # Paso 2: Parser METAR
        run_script("scripts/parse_metar_csv.py")

        # Paso 3: Unificación de AVWX + CORPAC
        run_script("scripts/merge_datasets.py")

        # Paso 4: Limpieza final AVWX + CORPAC
        run_script("scripts/clean_final_merged.py")

        # ✅ NUEVO PASO: Limpieza específica de OpenMeteo
        run_script("scripts/clean_openmeteo_data.py")

        # Paso 5: Evaluar estado de vuelos
        run_script("scripts/check_flight_status.py")
        
        # Paso 6: Pronóstico de visibilidad y techo de nubes
        run_script("forecast/train_forecast_model.py")
        run_script("forecast/predict_visibility_next_hour.py")
        run_script("forecast/train_cloudbase_forecast.py")
        run_script("forecast/predict_cloudbase_next_hour.py")
        
        # Paso 7: Generación de alertas
        run_script("scripts/generate_alerts.py")

        print(f"\n✅ Ciclo completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("⏳ Esperando 1 hora para el próximo ciclo...\n")
        time.sleep(3600)

if __name__ == "__main__":
    run_hourly_pipeline()
