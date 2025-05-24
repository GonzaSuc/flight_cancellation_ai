import pandas as pd
from datetime import datetime, timedelta
import re

# Rutas de los archivos
METAR_FILE = "data/processed/cleaned_weather_data.csv"
MINIMOS_FILE = "data/processed/minimos_operacionales.csv"
OUTPUT_FILE = "data/processed/estado_vuelos.csv"

# Tiempo de espera máximo en minutos antes de cancelar
TIEMPO_ESPERA_MIN = 60

# Cargar los datos
metar_df = pd.read_csv(METAR_FILE)
minimos_df = pd.read_csv(MINIMOS_FILE)

# Asegurar formato de fecha
metar_df['datetime'] = pd.to_datetime(metar_df['datetime'], format='mixed')

# Determinar qué columna usar como visibilidad
# Detectar columna de visibilidad disponible
if 'visibility' in metar_df.columns:
    vis_column = 'visibility'
elif 'visibility_x' in metar_df.columns:
    vis_column = 'visibility_x'
elif 'visibility_y' in metar_df.columns:
    vis_column = 'visibility_y'
else:
    raise ValueError("❌ No se encontró ninguna columna de visibilidad ('visibility', 'visibility_x' o 'visibility_y')")


# Función para extraer el techo de nubes (en pies) desde la columna de nubes (ej: SCT010, BKN007)
def extraer_techo_nubes(clouds_str):
    if pd.isna(clouds_str):
        return None
    capas = clouds_str.split(';')
    techos = []
    for capa in capas:
        match = re.search(r'(BKN|OVC)(\d{3})', capa)
        if match:
            techos.append(int(match.group(2)) * 100)  # convertir a pies
    return min(techos) if techos else None

# Inicializar lista de estados
estados = []

for _, row in metar_df.iterrows():
    estacion = row.get('station')
    visibilidad = row.get(vis_column, None)
    techo_nubes = extraer_techo_nubes(row.get('clouds', None))
    datetime_obs = row['datetime']

    # Buscar criterios mínimos para la estación
    criterios = minimos_df[minimos_df['airport'] == estacion]

    if criterios.empty or pd.isna(visibilidad):
        estados.append("⚠️ Sin criterio o visibilidad")
        continue

    # Seleccionar criterio de Categoría C (por ahora, simplificación)
    criterios_c = criterios[criterios['category'] == 'C']
    if criterios_c.empty:
        estados.append("⚠️ No hay criterio CAT C")
        continue

    criterio = criterios_c.iloc[0]
    min_vis = criterio.get('visibility', 99999)
    min_techo = criterio.get('MDAH', 0)  # mínima altitud de decisión o altura mínima de descenso

    try:
        vis_float = float(visibilidad)
    except:
        estados.append("⚠️ Visibilidad inválida")
        continue

    # Evaluar criterios: si visibilidad o techo están por debajo => NO operativo
    criterio_vis = vis_float >= float(min_vis)
    criterio_techo = (pd.isna(techo_nubes) or techo_nubes >= float(min_techo))

    if criterio_vis and criterio_techo:
        estados.append("✅ Operativo")
    else:
        # Revisar si ha persistido la condición en la última hora
        desde = datetime_obs - timedelta(minutes=TIEMPO_ESPERA_MIN)
        ultimos = metar_df[(metar_df['station'] == estacion) &
                           (metar_df['datetime'] >= desde)]

        bajos = ultimos[(pd.to_numeric(ultimos[vis_column], errors='coerce') < float(min_vis)) |
                        (ultimos['clouds'].apply(extraer_techo_nubes).fillna(99999) < float(min_techo))]

        if len(bajos) >= 2:
            estados.append("❌ Cancelado por mal clima")
        else:
            estados.append("⏳ En espera (condiciones bajo mínimo)")

# Agregar columna de resultados y guardar
metar_df['estado_vuelo'] = estados
metar_df.to_csv(OUTPUT_FILE, index=False)

print("✅ Evaluación completada para todas las filas. Resultados en:", OUTPUT_FILE)
