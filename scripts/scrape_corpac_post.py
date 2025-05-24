import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import os

def fetch_metars_corpac(codigos_oaci):
    print(f"🔎 Enviando POST con: {', '.join(codigos_oaci)}")

    url = "https://meteorologia.corpac.gob.pe/app/Meteorologia/tiempo/manualMetar.php"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "aeropT": " ".join(codigos_oaci),
        "incTAF": "on"
    }

    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        response.encoding = "utf-8"
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return []

    if response.status_code != 200:
        print(f"❌ Error HTTP: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    div_taf = soup.find("div", class_="taf")

    if not div_taf:
        print("❌ No se encontró el contenedor de METAR.")
        return []

    # Extrae todos los textos separados por saltos de línea
    lines = [line.strip() for line in div_taf.stripped_strings if "METAR" in line or any(code in line for code in codigos_oaci)]

    metars = []
    timestamp = datetime.utcnow()

    for line in lines:
        if "METAR:" in line:
            line = line.replace("METAR:", "").strip()
        parts = line.split()
        if len(parts) >= 2:
            station = parts[0]
            metars.append({
                "station": station,
                "metar": line,
                "datetime_scraped": timestamp
            })

    if not metars:
        print("⚠️ No se encontraron reportes METAR en el contenido.")
    else:
        print(f"✅ Se extrajeron {len(metars)} reportes METAR.")
    return metars


def guardar_metars_csv(metars, path="data/processed/corpac_metar_post.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df = pd.DataFrame(metars)
    if os.path.exists(path):
        df.to_csv(path, mode='a', header=False, index=False)
    else:
        df.to_csv(path, index=False)
    print(f"📁 Datos guardados en {path}")
    print(df)

if __name__ == "__main__":
    estaciones = ["SPQU", "SPRU", "SPZO", "SPJR", "SPHZ"]
    resultados = fetch_metars_corpac(estaciones)
    if resultados:
        guardar_metars_csv(resultados)
