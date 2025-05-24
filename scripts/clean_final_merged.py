# scripts/clean_final_merged.py

import pandas as pd
import os

def clean_final_dataset():
    print("🧹 Limpieza final de merged_weather_data.csv...")

    input_path = "data/processed/merged_weather_data.csv"
    output_path = "data/processed/cleaned_weather_data.csv"

    if not os.path.exists(input_path):
        print("❌ No se encontró el archivo merged_weather_data.csv")
        return

    df = pd.read_csv(input_path, parse_dates=["datetime"])

    # Eliminar duplicados exactos
    df = df.drop_duplicates()

    # Eliminar duplicados por station + datetime
    df = df.drop_duplicates(subset=["station", "datetime"])

    # Opcional: mantener solo filas con al menos 3 valores útiles meteorológicos
    meteo_cols = [
        "temperature_2m", "dew_point_2m", "cloudcover", "windspeed_10m", "windgusts_10m",
        "visibility", "precipitation", "pressure_msl", "wind_dir", "wind_speed", "clouds", "phenomena"
    ]
    available_cols = [c for c in meteo_cols if c in df.columns]
    df = df.dropna(subset=available_cols, thresh=3)

    # Ordenar
    df = df.sort_values(by=["station", "datetime"]).reset_index(drop=True)

    # Guardar archivo limpio
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✅ Archivo limpio guardado como: {output_path} ({len(df)} filas)")

if __name__ == "__main__":
    clean_final_dataset()
