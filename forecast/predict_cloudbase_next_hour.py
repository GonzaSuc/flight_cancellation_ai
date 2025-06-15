# forecast/predict_cloudbase_next_hour.py

import pandas as pd
import joblib
import os
from datetime import datetime

print("🔍 Leyendo datos de OpenMeteo para predicción de techo de nubes...")

# Archivos necesarios
MODEL_FILE = "forecast/models/stacked_cloudbase_model.pkl"
SCALER_FILE = "forecast/models/cloudbase_scaler.pkl"
METAR_FILE = "data/processed/cleaned_weather_data.csv"
OPENMETEO_FILE = "data/processed/cleaned_openmeteo_data.csv"
OUTPUT_FILE = "forecast/predicted_cloudbase.csv"

# Verificar existencia
if not os.path.exists(MODEL_FILE) or not os.path.exists(SCALER_FILE):
    raise FileNotFoundError("❌ Modelo o scaler no encontrados.")

# Cargar modelo y scaler
model = joblib.load(MODEL_FILE)
scaler = joblib.load(SCALER_FILE)

# Cargar datos reales de AVWX/CORPAC (hoy)
df_metar = pd.read_csv(METAR_FILE, parse_dates=["datetime"])
df_metar = df_metar[df_metar["datetime"].dt.date == datetime.utcnow().date()]
ultimos = df_metar.sort_values("datetime").groupby("station").tail(1)

if ultimos.empty:
    raise ValueError("❌ No hay datos actuales de AVWX/CORPAC para hoy.")

# Cargar datos de OpenMeteo (para buscar condiciones futuras)
df_meteo = pd.read_csv(OPENMETEO_FILE, parse_dates=["datetime"])
df_meteo = df_meteo[df_meteo["datetime"].dt.date == datetime.utcnow().date()]
df_meteo = df_meteo.sort_values(["station", "datetime"])


df_meteo = df_meteo[df_meteo["datetime"].notnull()].sort_values("datetime")
ultimos = ultimos[ultimos["datetime"].notnull()].sort_values("datetime")

# Convertir a hora local (UTC-5)
ultimos["datetime"] = pd.to_datetime(ultimos["datetime"]) - pd.Timedelta(hours=5)

# Filtrar por fecha local actual
hoy = pd.Timestamp.now().date()
ultimos = ultimos[ultimos["datetime"].dt.date == hoy]


# Merge para unir último dato real con la próxima predicción horaria
merged = pd.merge_asof(
    ultimos.sort_values(["station", "datetime"]),
    df_meteo,
    on="datetime",
    by="station",
    direction="forward",
    tolerance=pd.Timedelta("1h")
)

# Filtrar columnas requeridas
features = ["temperature_2m", "dew_point_2m", "cloudcover", "windspeed_10m",
            "windgusts_10m", "precipitation", "pressure_msl"]
X = merged[features]    
# Eliminar filas con NaN
X = X.dropna()
ultimos = ultimos.loc[X.index]

# Verificar si hay datos suficientes para predecir
if X.empty:
    print("❌ No hay datos válidos disponibles para hacer la predicción de techo de nubes.")
    exit()

# Escalar los datos
X_scaled = scaler.transform(X)

# Realizar predicción
pred = model.predict(X_scaled)
ultimos['cloudbase_t+1'] = pred

X_scaled = scaler.transform(X)

# Eliminar filas con NaN antes de la predicción
X = X.dropna()
ultimos = ultimos.loc[X.index]
X_scaled = scaler.transform(X)


# Predicción
pred = model.predict(X_scaled)
merged["cloudbase_t+1"] = pred

# Guardar resultado
merged[["station", "datetime", "cloudbase_t+1"]].to_csv(OUTPUT_FILE, index=False)
print(f"✅ Predicción guardada en: {OUTPUT_FILE}")
