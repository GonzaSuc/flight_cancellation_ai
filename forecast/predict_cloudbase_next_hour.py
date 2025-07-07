# forecast/predict_cloudbase_next_hour.py

import pandas as pd
import joblib
import os

print("🔍 Iniciando predicción de techo de nubes...")

# Rutas
MODEL_FILE = "forecast/models/stacked_cloudbase_model.pkl"
SCALER_FILE = "forecast/models/cloudbase_scaler.pkl"
INPUT_FILE = "data/processed/cleaned_openmeteo_data.csv"
OUTPUT_FILE = "forecast/output/cloudbase_forecast.csv"
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# Cargar modelo y escalador
model = joblib.load(MODEL_FILE)
scaler = joblib.load(SCALER_FILE)

# Cargar datos
df_forecast = pd.read_csv(INPUT_FILE)
df_forecast["datetime"] = pd.to_datetime(df_forecast["datetime"], errors="coerce")
df_forecast.sort_values(["station", "datetime"], inplace=True)

# Usar la fila más reciente por estación
latest_data = df_forecast.groupby("station").tail(1).copy()

# Features del modelo
features = ['temperature_2m', 'dew_point_2m', 'cloudcover',
            'windspeed_10m', 'windgusts_10m', 'precipitation', 'pressure_msl']

# Filtrar y escalar
latest_data.dropna(subset=features, inplace=True)
X = scaler.transform(latest_data[features])

# Predecir techo de nubes a +1h
latest_data["predicted_clouds_t+1"] = model.predict(X)

# Renombrar columna cloudcover a clouds
latest_data["clouds"] = latest_data["cloudcover"]

# Guardar solo columnas necesarias
latest_data[['station', 'datetime', 'clouds', 'predicted_clouds_t+1']].to_csv(OUTPUT_FILE, index=False)

print("✅ Predicción completada. Resultados guardados en:", OUTPUT_FILE)
