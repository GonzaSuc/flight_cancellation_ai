# scripts/parse_metar_csv.py

import pandas as pd
import re
import os

def parse_metar_line(metar):
    result = {
        "wind_dir": None,
        "wind_speed": None,
        "visibility": None,
        "clouds": None,
        "phenomena": None,
        "intensity_prefix": None,
    }

    # Dirección y velocidad del viento
    wind_match = re.search(r'(\d{3}|VRB)(\d{2})KT', metar)
    if wind_match:
        result["wind_dir"] = wind_match.group(1)
        result["wind_speed"] = int(wind_match.group(2))

    # Visibilidad en metros
    vis_match = re.search(r'\s(\d{4})\s', metar)
    if vis_match:
        result["visibility"] = int(vis_match.group(1))

    # Nubes (primer reporte encontrado)
    cloud_match = re.findall(r'\b(FEW|SCT|BKN|OVC|VV)(\d{3})\b', metar)
    if cloud_match:
        result["clouds"] = ";".join([f"{c[0]}{c[1]}" for c in cloud_match])

    # Fenómenos meteorológicos
    wx_match = re.findall(r'\b(-|\+|RE|VC|MI|BC|BL|DR|SH|TS|FZ)?(DZ|RA|SN|SG|IC|PL|GR|GS|UP|BR|FG|FU|VA|DU|SA|HZ|PY|PO|SQ|FC|SS|DS)', metar)
    if wx_match:
        result["phenomena"] = ";".join(set([w[1] for w in wx_match]))
        result["intensity_prefix"] = ";".join(set([w[0] for w in wx_match if w[0]]))

    return result

def process_metar_file(input_path, output_path, metar_column):
    df = pd.read_csv(input_path)

    print(f"📑 Procesando {input_path}...")

    parsed_rows = []
    for i, row in df.iterrows():
        metar = row.get(metar_column, "")
        if pd.isna(metar) or not isinstance(metar, str):
            continue

        parsed = parse_metar_line(metar)

        parsed_row = {
            "station": row.get("station") or metar[:4],
            "datetime": row.get("datetime_scraped") or row.get("observed") or None,
            **parsed
        }

        parsed_rows.append(parsed_row)

    df_parsed = pd.DataFrame(parsed_rows)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_parsed.to_csv(output_path, index=False)
    print(f"✅ Guardado en {output_path} ({len(df_parsed)} filas)")

if __name__ == "__main__":
    process_metar_file("data/processed/avwx_metar.csv", "data/processed/avwx_parsed.csv", "raw_metar")
    process_metar_file("data/processed/corpac_metar_post.csv", "data/processed/corpac_parsed.csv", "metar")
