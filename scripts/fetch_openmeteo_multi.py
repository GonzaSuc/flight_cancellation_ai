# scripts/fetch_openmeteo_multi.py

import requests
import pandas as pd
from datetime import datetime
import os

AIRPORTS = {
    "SPQU": (-16.3411, -71.5831),
    "SPRU": (-8.0814, -79.1088),
    "SPZO": (-13.5357, -71.9388),
    "SPJR": (-7.1392, -78.4894),
    "SPHZ": (-9.3474, -77.5983),
}

VARS = [
    "temperature_2m", "dew_point_2m", "cloudcover",
    "windspeed_10m", "windgusts_10m", "visibility",
    "precipitation", "pressure_msl"
]

def fetch_openmeteo_data():
    rows = []
    for code, coords in AIRPORTS.items():
        print(f"📡 Consultando datos para {code}...")
        lat, lon = coords
        url = (
             f"https://api.open-meteo.com/v1/forecast"
             f"?latitude={lat}&longitude={lon}"
             f"&hourly=temperature_2m,dew_point_2m,cloudcover,windspeed_10m,windgusts_10m,visibility,precipitation,pressure_msl"
             f"&timezone=auto"
)

        try:
            response = requests.get(url)
            data = response.json()
            hours = data["hourly"]["time"]

            for i, time_str in enumerate(hours):
                row = {
                    "station": code,
                    "datetime": time_str,
                }
                for var in VARS:
                    row[var] = data["hourly"][var][i]
                rows.append(row)

        except Exception as e:
            print(f"❌ Error al obtener datos para {code}: {e}")

    # Guardar en CSV
    df = pd.DataFrame(rows)
    os.makedirs("data/processed", exist_ok=True)
    output_path = "data/processed/openmeteo_data.csv"

    if os.path.exists(output_path):
        df.to_csv(output_path, mode="a", header=False, index=False)
    else:
        df.to_csv(output_path, index=False)

    print(f"✅ Datos guardados en {output_path} (filas: {len(df)})")

if __name__ == "__main__":
    fetch_openmeteo_data()
