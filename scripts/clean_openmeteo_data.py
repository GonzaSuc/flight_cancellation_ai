# scripts/clean_openmeteo_data.py

import pandas as pd
import os

def clean_openmeteo_dataset():
    print("🧹 Limpieza exclusiva de OpenMeteo...")

    input_path = "data/processed/openmeteo_data.csv"
    output_path = "data/processed/cleaned_openmeteo_data.csv"

    if not os.path.exists(input_path):
        print("❌ No se encontró el archivo openmeteo_data.csv")
        return

    df = pd.read_csv(input_path, parse_dates=["datetime"])

    # Eliminar duplicados exactos
    df = df.drop_duplicates()

    # Eliminar duplicados por station + datetime
    df = df.drop_duplicates(subset=["station", "datetime"])

    # Validar columnas meteorológicas típicas de OpenMeteo
    meteo_cols = [
        "temperature_2m", "dew_point_2m", "cloudcover", "windspeed_10m",
        "windgusts_10m", "visibility", "precipitation", "pressure_msl"
    ]
    available_cols = [c for c in meteo_cols if c in df.columns]

    # Requiere al menos 3 variables válidas
    df = df.dropna(subset=available_cols, thresh=3)

    # Ordenar por estación y fecha
    df = df.sort_values(by=["station", "datetime"]).reset_index(drop=True)

    # Guardar como nuevo CSV exclusivo
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✅ Datos limpios de OpenMeteo guardados en: {output_path} ({len(df)} filas)")

if __name__ == "__main__":
    clean_openmeteo_dataset()
