import pandas as pd
from datetime import datetime, timedelta
import re

METAR_FILE = "data/processed/cleaned_weather_data.csv"
MINIMOS_FILE = "data/processed/minimos_operacionales.csv"
OUTPUT_FILE = "data/processed/estado_vuelos.csv"

TIEMPO_ESPERA_MIN = 60  # en minutos

# Leer y preparar datos
metar_df = pd.read_csv(METAR_FILE)
minimos_df = pd.read_csv(MINIMOS_FILE)
metar_df['datetime'] = pd.to_datetime(metar_df['datetime'], format='mixed')

# Detectar columna de visibilidad
if 'visibility' in metar_df.columns:
    vis_column = 'visibility'
elif 'visibility_x' in metar_df.columns:
    vis_column = 'visibility_x'
elif 'visibility_y' in metar_df.columns:
    vis_column = 'visibility_y'
else:
    raise ValueError("❌ No se encontró columna de visibilidad")

# Función para techo de nubes
def extraer_techo_nubes(clouds_str):
    if pd.isna(clouds_str): return None
    capas = clouds_str.split(';')
    techos = [int(m.group(2)) * 100 for capa in capas if (m := re.search(r'(BKN|OVC)(\d{3})', capa.strip()))]
    return min(techos) if techos else None

# Aplicar techo
metar_df = metar_df.sort_values(by=['station', 'datetime']).reset_index(drop=True)
metar_df['techo_nubes'] = metar_df['clouds'].apply(extraer_techo_nubes)

# Inicializar estructuras
estados = []
estado_anterior = {}
tiempo_espera = {}

for _, row in metar_df.iterrows():
    estacion = row['station']
    fecha = row['datetime']
    vis = row[vis_column]
    techo = row['techo_nubes']

    criterios = minimos_df[(minimos_df['airport'] == estacion) & (minimos_df['category'] == 'C')]

    if criterios.empty or pd.isna(vis):
        estados.append("⚠ Sin criterio o visibilidad")
        estado_anterior[estacion] = None
        tiempo_espera[estacion] = None
        continue

    criterio = criterios.iloc[0]
    min_vis = float(criterio['visibility'])
    min_techo = pd.to_numeric(criterio['MDAH'], errors='coerce')

    try:
        vis = float(vis)
    except:
        estados.append("⚠ Visibilidad inválida")
        estado_anterior[estacion] = None
        tiempo_espera[estacion] = None
        continue

    cumple_vis = vis >= min_vis
    cumple_techo = pd.notna(techo) and techo >= min_techo
    condiciones_ok = cumple_vis and cumple_techo

    # Si condiciones buenas => operativo
    if condiciones_ok:
        estados.append("✅ Operativo")
        estado_anterior[estacion] = "operativo"
        tiempo_espera[estacion] = None
        continue

    # Condiciones malas
    if estado_anterior.get(estacion) == "cancelado":
        estados.append("❌ Cancelado por mal clima")  # Regla 2
        continue

    if estado_anterior.get(estacion) != "en espera":
        estados.append("⏳ En espera (condiciones bajo mínimo)")
        estado_anterior[estacion] = "en espera"
        tiempo_espera[estacion] = fecha
    else:
        inicio = tiempo_espera.get(estacion)
        if inicio and (fecha - inicio).total_seconds() >= TIEMPO_ESPERA_MIN * 60:
            estados.append("❌ Cancelado por mal clima")
            estado_anterior[estacion] = "cancelado"
        else:
            estados.append("⏳ En espera (condiciones bajo mínimo)")

# Guardar resultados
metar_df['estado_vuelo'] = estados
metar_df.to_csv(OUTPUT_FILE, index=False)
print("✅ Evaluación completada. Resultados guardados en:", OUTPUT_FILE)