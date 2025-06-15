# forecast/check_future_flight_status.py

import pandas as pd
import os

PRONOSTICO_FILE = "forecast/predicted_visibility.csv"
MINIMOS_FILE = "data/processed/minimos_operacionales.csv"
OUTPUT_FILE = "forecast/estado_pronosticado.csv"

# Leer archivos
if not os.path.exists(PRONOSTICO_FILE):
    raise FileNotFoundError("❌ No se encontró el archivo de visibilidad pronosticada.")

if not os.path.exists(MINIMOS_FILE):
    raise FileNotFoundError("❌ No se encontró el archivo de mínimos operacionales.")

df_vis = pd.read_csv(PRONOSTICO_FILE)
df_min = pd.read_csv(MINIMOS_FILE)

# Asegurar columnas correctas
df_vis.columns = ['station', 'datetime', 'visibility_forecast']
df_min = df_min[df_min['category'] == 'C']

# Evaluar cada aeropuerto
estados = []
for _, row in df_vis.iterrows():
    oaci = row['station']
    vis_pronostico = row['visibility_forecast']

    criterio = df_min[df_min['airport'] == oaci]

    if criterio.empty:
        estados.append("⚠️ Sin criterio disponible")
        continue

    min_vis = criterio.iloc[0]['visibility']

    if vis_pronostico >= min_vis:
        estados.append("✅ Se mantendrá operativo")
    elif vis_pronostico >= min_vis * 0.9:
        estados.append("⏳ En espera (pronóstico bajo mínimo)")
    else:
        estados.append("❌ Probable cancelación en 1h")

# Guardar resultado
df_vis['estado_pronosticado'] = estados
df_vis.to_csv(OUTPUT_FILE, index=False)

print(f"✅ Evaluación futura completada. Resultados guardados en: {OUTPUT_FILE}")
