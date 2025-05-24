# scripts/merge_datasets.py

import pandas as pd
from pathlib import Path

# Rutas de los archivos
AVWX_FILE = "data/processed/avwx_parsed.csv"
CORPAC_FILE = "data/processed/corpac_parsed.csv"
OUTPUT_FILE = "data/processed/merged_weather_data.csv"

def merge_datasets():
    print("🔗 Uniendo datasets METAR (AVWX + CORPAC)...")

    # Leer archivos
    df_avwx = pd.read_csv(AVWX_FILE)
    df_corpac = pd.read_csv(CORPAC_FILE)

    # Concatenar sin Open-Meteo
    merged = pd.concat([df_avwx, df_corpac], ignore_index=True)

    # Guardar archivo combinado
    Path(OUTPUT_FILE).parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(OUTPUT_FILE, index=False)

    print(f"✅ Datos combinados guardados en {OUTPUT_FILE} ({len(merged)} filas)")

if __name__ == "__main__":
    merge_datasets()
