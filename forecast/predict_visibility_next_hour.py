# forecast/predict_visibility_next_hour.py

import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
import os

# Rutas de archivos
MODEL_FILE = "forecast/models/stacked_visibility_model.pkl"
SCALER_FILE = "forecast/models/visibility_scaler.pkl"
INPUT_FILE = "data/processed/cleaned_weather_data.csv"
OUTPUT_FILE = "forecast/output/visibility_forecast.csv"
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# Cargar modelo y scaler
model = joblib.load(MODEL_FILE)
scaler = joblib.load(SCALER_FILE)

# Leer datos
df = pd.read_csv(INPUT_FILE)
df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
df = df.sort_values(by=['station', 'datetime'])

# Reemplazar y convertir columnas necesarias
df['wind_dir'] = df['wind_dir'].replace('VRB', 0)
df['wind_dir'] = pd.to_numeric(df['wind_dir'], errors='coerce')
df['wind_speed'] = pd.to_numeric(df['wind_speed'], errors='coerce')
df['visibility'] = pd.to_numeric(df['visibility'], errors='coerce')

# Eliminar nulos
df.dropna(subset=['station', 'datetime', 'wind_dir', 'wind_speed', 'visibility'], inplace=True)

# Tomar solo el último registro por estación para predecir visibilidad t+1
latest = df.groupby('station').tail(1).copy()

# Features
features = ['wind_dir', 'wind_speed', 'visibility']
X_latest = latest[features]
X_scaled = scaler.transform(X_latest)

# Predicción
latest['predicted_visibility_t+1'] = model.predict(X_scaled)

# Guardar solo columnas solicitadas
latest[['station', 'datetime', 'visibility', 'predicted_visibility_t+1']].to_csv(OUTPUT_FILE, index=False)

print("✅ Forecast completed. Results saved to:", OUTPUT_FILE)
