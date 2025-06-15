# scripts/generate_alerts.py

import pandas as pd
import os

print("📡 Generando alertas a partir del pronóstico...")

# Archivos de entrada
cloudbase_file = "forecast/predicted_cloudbase.csv"
visibility_file = "forecast/predicted_visibility.csv"
minimos_file = "data/processed/minimos_operacionales.csv"
output_file = "forecast/alerts.csv"

# Verificar existencia
for file in [cloudbase_file, visibility_file, minimos_file]:
    if not os.path.exists(file):
        print(f"❌ Archivo faltante: {file}")
        exit()

# Cargar datos
df_cld = pd.read_csv(cloudbase_file)
df_vis = pd.read_csv(visibility_file)
df_min = pd.read_csv(minimos_file)

# Renombrar columnas
df_cld = df_cld.rename(columns={"cloudbase_t+1": "cloudbase"})
df_vis = df_vis.rename(columns={"predicted_visibility_next_hour": "visibility"})
df_min = df_min.rename(columns={"visibility": "min_visibility", "MDAH": "min_cloudbase"})

# Unir visibilidad y techo por estación y datetime
df = pd.merge(df_cld, df_vis, on=["station", "datetime"], how="inner")

# Unir con mínimos por estación
df = pd.merge(df, df_min[["airport", "min_cloudbase", "min_visibility"]], left_on="station", right_on="airport", how="left")

# Rellenar NaNs
df["min_cloudbase"] = df["min_cloudbase"].fillna(300)
df["min_visibility"] = df["min_visibility"].fillna(1500)

# Clasificar alertas
def clasificar_alerta(row):
    if row["cloudbase"] < row["min_cloudbase"] or row["visibility"] < row["min_visibility"]:
        return "❌ Riesgo alto de cancelación"
    elif row["cloudbase"] < row["min_cloudbase"] + 100 or row["visibility"] < row["min_visibility"] + 1000:
        return "⏳ Condiciones bajo mínimo"
    else:
        return "✅ Condiciones buenas"

df["alerta"] = df.apply(clasificar_alerta, axis=1)

# Exportar columnas finales
df_resultado = df[["station", "datetime", "cloudbase", "visibility", "alerta"]]
df_resultado.to_csv(output_file, index=False)
print(f"✅ Alertas generadas en: {output_file}")
