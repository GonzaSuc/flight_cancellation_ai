import pandas as pd
import os

# Archivos
VIS_FILE = "forecast/output/visibility_forecast.csv"
CLOUD_FILE = "forecast/output/cloudbase_forecast.csv"
MINIMOS_FILE = "data/processed/minimos_operacionales.csv"
OUTPUT_FILE = "forecast/estado_pronosticado.csv"

# Verificar existencia de archivos
for f in [VIS_FILE, CLOUD_FILE, MINIMOS_FILE]:
    if not os.path.exists(f):
        raise FileNotFoundError(f"❌ No se encontró el archivo: {f}")

# Leer pronósticos
df_vis = pd.read_csv(VIS_FILE)
df_cloud = pd.read_csv(CLOUD_FILE)
df_min = pd.read_csv(MINIMOS_FILE)

# Filtrar solo categoría C
df_min = df_min[df_min['category'] == 'C']

# Renombrar columnas
df_vis.columns = ['station', 'datetime', 'visibility_forecast']
df_cloud.columns = ['station', 'datetime', 'cloudbase_forecast']

# Unir visibilidad y techo
df = pd.merge(df_vis, df_cloud, on=['station', 'datetime'], how='inner')

# Asegurar que los datos sean numéricos
df['visibility_forecast'] = pd.to_numeric(df['visibility_forecast'], errors='coerce')
df['cloudbase_forecast'] = pd.to_numeric(df['cloudbase_forecast'], errors='coerce')
df_min['visibility'] = pd.to_numeric(df_min['visibility'], errors='coerce')
df_min['MDAH'] = pd.to_numeric(df_min['MDAH'], errors='coerce')

# Unir con los mínimos
df = pd.merge(df, df_min[['airport', 'visibility', 'MDAH']], left_on='station', right_on='airport', how='left')

# Evaluar condiciones
def evaluar_estado(row):
    if pd.isna(row['visibility']) or pd.isna(row['MDAH']):
        return "⚠️ Sin criterio disponible"
    
    cumple_vis = row['visibility_forecast'] >= row['visibility']
    cumple_techo = row['cloudbase_forecast'] >= row['MDAH']

    if cumple_vis and cumple_techo:
        return "✅ Se mantendrá operativo"
    elif (
        row['visibility_forecast'] >= row['visibility'] * 0.9 or 
        row['cloudbase_forecast'] >= row['MDAH'] * 0.9
    ):
        return "⏳ En espera (pronóstico bajo mínimo)"
    else:
        return "❌ Probable cancelación en 1h"

# Aplicar evaluación
df['estado_pronosticado'] = df.apply(evaluar_estado, axis=1)

# Guardar resultado
df.to_csv(OUTPUT_FILE, index=False)
print(f"✅ Evaluación futura completada. Resultados guardados en: {OUTPUT_FILE}")