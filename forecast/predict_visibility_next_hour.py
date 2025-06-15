import pandas as pd
import joblib
import os
from datetime import datetime

# Rutas
CORPAC_AVWX_FILE = "data/processed/cleaned_weather_data.csv"
OPENMETEO_FILE = "data/processed/cleaned_openmeteo_data.csv"
MODEL_FILE = "forecast/models/stacked_visibility_model.pkl"
SCALER_FILE = "forecast/models/visibility_scaler.pkl"
OUTPUT_FILE = "forecast/predicted_visibility.csv"

# Validaciones
for f in [CORPAC_AVWX_FILE, OPENMETEO_FILE, MODEL_FILE, SCALER_FILE]:
    if not os.path.exists(f):
        raise FileNotFoundError(f"❌ Archivo faltante: {f}")

# Cargar datasets
df_metar = pd.read_csv(CORPAC_AVWX_FILE)
df_metar['datetime'] = pd.to_datetime(df_metar['datetime'], errors='coerce')
df_metar = df_metar.dropna(subset=["datetime"])

df_openmeteo = pd.read_csv(OPENMETEO_FILE, parse_dates=["datetime"])

# Filtrar observaciones de HOY desde AVWX/CORPAC
hoy = datetime.now().date()
df_hoy = df_metar[df_metar['datetime'].dt.date == hoy]

# Tomar la última observación real de hoy por estación
df_actual = df_hoy.sort_values("datetime").groupby("station").tail(1).copy()

if df_actual.empty:
    raise ValueError("❌ No se encontraron datos de AVWX/CORPAC con fecha de hoy.")

# Vincular con datos meteorológicos de OpenMeteo por cercanía de fecha/hora
df = pd.merge_asof(
    df_actual.sort_values("datetime"),
    df_openmeteo.sort_values("datetime"),
    on="datetime",
    by="station",
    direction="nearest",
    tolerance=pd.Timedelta("1H")
)

if df.empty:
    raise ValueError("❌ No se pudieron alinear datos de OpenMeteo con observaciones actuales.")

# Features para predicción
features = ['temperature_2m', 'dew_point_2m', 'cloudcover', 'windspeed_10m',
            'windgusts_10m', 'precipitation', 'pressure_msl']

X = df[features]

# Cargar modelo y scaler
scaler = joblib.load(SCALER_FILE)
model = joblib.load(MODEL_FILE)

X_scaled = scaler.transform(X)

# Predicción
df['predicted_visibility_next_hour'] = model.predict(X_scaled)

# Exportar resultados
df[['station', 'datetime', 'predicted_visibility_next_hour']].to_csv(OUTPUT_FILE, index=False)
print("✅ Predicción completada solo con datos reales de hoy. Guardado en:", OUTPUT_FILE)
