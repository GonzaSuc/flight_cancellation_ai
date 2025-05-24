import requests
import pandas as pd
from datetime import datetime
import os

API_KEY = "8mjd_fG_m6fJXy_4Z_COca-kuqOcnZmlmjB3UsHsAvc"  # ⚠️ Reemplaza esto con tu API key de AVWX
BASE_URL = "https://avwx.rest/api/metar"

HEADERS = {
    "Authorization": API_KEY
}

STATIONS = ["SPQU", "SPRU", "SPZO", "SPJR", "SPHZ"]

def fetch_metar(station):
    url = f"{BASE_URL}/{station}?format=json"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "station": station,
                "raw_metar": data.get("raw", ""),
                "datetime_scraped": datetime.utcnow(),
                "observed": data.get("time", {}).get("dt", ""),
                "temperature": data.get("temperature", {}).get("value"),
                "dewpoint": data.get("dewpoint", {}).get("value"),
                "wind_speed": data.get("wind_speed", {}).get("value"),
                "wind_direction": data.get("wind_direction", {}).get("value"),
                "visibility": data.get("visibility", {}).get("value"),
                "altimeter": data.get("altimeter", {}).get("value"),
                "flight_rules": data.get("flight_rules")
            }
        else:
            print(f"❌ {station}: Error HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ {station}: {e}")
        return None

def main():
    os.makedirs("data/processed", exist_ok=True)
    output_file = "data/processed/avwx_metar.csv"
    records = []

    for station in STATIONS:
        print(f"🔍 Recolectando METAR de {station}...")
        metar = fetch_metar(station)
        if metar:
            records.append(metar)

    if not records:
        print("⚠️ No se recolectaron datos.")
        return

    df = pd.DataFrame(records)

    if os.path.exists(output_file):
        df.to_csv(output_file, mode='a', header=False, index=False)
    else:
        df.to_csv(output_file, index=False)

    print(f"✅ Se guardaron {len(df)} registros en {output_file}")
    print(df)

if __name__ == "__main__":
    main()
