import pandas as pd
import os

def clean_final_dataset():
    print("🧹 Limpieza final de merged_weather_data.csv con relleno desde OpenMeteo...")

    input_path = "data/processed/merged_weather_data.csv"
    meteo_path = "data/processed/cleaned_openmeteo_data.csv"
    output_path = "data/processed/cleaned_weather_data.csv"

    if not os.path.exists(input_path):
        print("❌ No se encontró el archivo merged_weather_data.csv")
        return

    df = pd.read_csv(input_path)
    meteo = pd.read_csv(meteo_path)

    # Convertir datetime correctamente
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    meteo['datetime'] = pd.to_datetime(meteo['datetime'], errors='coerce')

    # Eliminar duplicados
    df = df.drop_duplicates()
    df = df.drop_duplicates(subset=["station", "datetime"])

    original_rows = len(df)

    meteo_cols = [
        "temperature_2m", "dew_point_2m", "cloudcover", "windspeed_10m", "windgusts_10m",
        "visibility", "precipitation", "pressure_msl", "wind_dir", "wind_speed", "clouds", "phenomena"
    ]
    available_cols = [c for c in meteo_cols if c in df.columns]

    # Detectar filas incompletas
    df_incomplete = df[df[available_cols].isnull().sum(axis=1) > (len(available_cols) - 3)]
    df_complete = df[df[available_cols].isnull().sum(axis=1) <= (len(available_cols) - 3)]

    if not df_incomplete.empty:
        print(f"🔄 Rellenando {len(df_incomplete)} filas incompletas desde OpenMeteo...")

        # Asegurar orden por merge_asof
        df_incomplete = df_incomplete.sort_values("datetime")
        meteo = meteo.sort_values("datetime")

        # merge_asof con datetime correcto
        merged = pd.merge_asof(
            df_incomplete,
            meteo,
            on="datetime",
            by="station",
            direction="nearest",
            tolerance=pd.Timedelta("1h")
        )

        # Rellenar columnas
        for col in meteo_cols:
            col_x, col_y = col + "_x", col + "_y"
            if col_x in merged.columns and col_y in merged.columns:
                merged[col_x].fillna(merged[col_y], inplace=True)

        # Renombrar columnas resultantes
        merged.rename(columns={col + "_x": col for col in meteo_cols if col + "_x" in merged.columns}, inplace=True)
        merged = merged[df.columns]  # conservar solo columnas originales

        df = pd.concat([df_complete, merged], ignore_index=True)

    else:
        df = df_complete

    df = df.sort_values(by=["station", "datetime"]).reset_index(drop=True)

    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✅ Archivo limpio guardado como: {output_path} ({len(df)} filas, antes: {original_rows})")

if __name__ == "__main__":
    clean_final_dataset()
