# forecast/predict_cloudbase_next_hour.py

import pandas as pd
import joblib
from datetime import datetime

print("🔍 Iniciando predicción de techo de nubes...")

# Cargar modelo y escalador
model = joblib.load("forecast/models/stacked_cloudbase_model.pkl")
scaler = joblib.load("forecast/models/cloudbase_scaler.pkl")

# Cargar datos
df_forecast = pd.read_csv("data/processed/cleaned_openmeteo_data.csv")
df_forecast["datetime"] = pd.to_datetime(df_forecast["datetime"])

# Ordenar antes del merge_asof (necesario aunque solo uses un dataset)
df_forecast.sort_values(["station", "datetime"], inplace=True)

# Usar la fila más reciente por estación
latest_data = df_forecast.groupby("station").tail(1)

# Features del modelo
features = ['temperature_2m', 'dew_point_2m', 'cloudcover',
            'windspeed_10m', 'windgusts_10m', 'precipitation', 'pressure_msl']

# Filtrar y escalar
latest_data.dropna(subset=features, inplace=True)
X = scaler.transform(latest_data[features])

# Predecir techo de nubes a +1h
pred = model.predict(X)
latest_data["predicted_cloudbase_t+1"] = pred

# Mostrar resultados por estación
for station in latest_data["station"]:
    cb = latest_data[latest_data["station"] == station]["predicted_cloudbase_t+1"].iloc[0]
    print(f"☁️ {station}: Predicción de techo de nubes (t+1h) → {cb:.2f} m")
