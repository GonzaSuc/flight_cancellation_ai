import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, StackingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from math import sqrt
import joblib

# Archivos de entrada y salida
AVWX_CORPAC_FILE = "data/processed/cleaned_weather_data.csv"
OPENMETEO_FILE = "data/processed/cleaned_openmeteo_data.csv"
MODEL_FILE = "forecast/models/stacked_visibility_model.pkl"
SCALER_FILE = "forecast/models/visibility_scaler.pkl"

# Crear carpeta si no existe
os.makedirs(os.path.dirname(MODEL_FILE), exist_ok=True)

# Cargar los datasets
df_metar = pd.read_csv(AVWX_CORPAC_FILE)
df_meteo = pd.read_csv(OPENMETEO_FILE)

# Convertir datetime correctamente
df_metar['datetime'] = pd.to_datetime(df_metar['datetime'], errors='coerce')
df_meteo['datetime'] = pd.to_datetime(df_meteo['datetime'], errors='coerce')

# Convertir a datetime con formato seguro y eliminar nulos
df_metar['datetime'] = pd.to_datetime(df_metar['datetime'], errors='coerce')
df_meteo['datetime'] = pd.to_datetime(df_meteo['datetime'], errors='coerce')

df_metar = df_metar.dropna(subset=['datetime'])
df_meteo = df_meteo.dropna(subset=['datetime'])

# Ordenar por estación y tiempo
df_metar = df_metar.sort_values(["station", "datetime"])
df_meteo = df_meteo.sort_values(["station", "datetime"])

# Merge asof por estación con tolerancia de 1 hora
merged_list = []

for station in df_metar['station'].unique():
    metar_station = df_metar[df_metar['station'] == station]
    meteo_station = df_meteo[df_meteo['station'] == station]

    # Asegurar que ambos tengan datos antes de mergear
    if len(metar_station) > 0 and len(meteo_station) > 0:
        merged = pd.merge_asof(
            metar_station,
            meteo_station,
            on="datetime",
            tolerance=pd.Timedelta("1h"),
            direction="nearest"
        )
        merged['station'] = station  # Reafirmar la estación por si se pierde
        merged_list.append(merged)

# Concatenar todo
df = pd.concat(merged_list, ignore_index=True)


# Agrupar por estación y aplicar merge_asof con tolerancia
merged_list = []

for station in df_metar['station'].unique():
    metar_station = df_metar[df_metar['station'] == station]
    meteo_station = df_meteo[df_meteo['station'] == station]

    merged = pd.merge_asof(
        metar_station,
        meteo_station,
        on="datetime",
        tolerance=pd.Timedelta("1h"),
        direction="nearest"
    )
    merged['station'] = station  # Reasignar estación (puede perderse si meteo no tiene match)
    merged_list.append(merged)

df = pd.concat(merged_list, ignore_index=True)


# Asegurar que visibility_y existe (de openmeteo)
if 'visibility_y' not in df.columns:
    raise ValueError("❌ No se encontró 'visibility_y' en el dataframe. Verifica el merge.")

# Crear columna de visibilidad futura
df["visibility_t+1"] = df.groupby("station")["visibility_y"].shift(-1)

# Eliminar nulos (del shift o valores faltantes)
df.dropna(subset=['visibility_t+1'], inplace=True)

# Features desde OpenMeteo
features = ['temperature_2m', 'dew_point_2m', 'cloudcover',
            'windspeed_10m', 'windgusts_10m', 'precipitation', 'pressure_msl']

df = df.dropna(subset=features + ["visibility_t+1"])

X = df[features]
y = df['visibility_t+1']

# Escalar
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# División train/test
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Modelos base
base_models = [
    ('rf', RandomForestRegressor(n_estimators=100, random_state=42)),
    ('gb', GradientBoostingRegressor(n_estimators=100, random_state=42)),
    ('knn', KNeighborsRegressor(n_neighbors=5))
]

# Meta-modelo
meta_model = Ridge()

# Stacking
stack = StackingRegressor(
    estimators=base_models,
    final_estimator=meta_model,
    cv=5,
    n_jobs=-1
)

# Entrenar
stack.fit(X_train, y_train)

# Evaluación
y_pred = stack.predict(X_test)
rmse = sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("📊 Modelo de pronóstico de visibilidad (stacking)")
print(f"✅ RMSE: {rmse:.2f}")
print(f"✅ R² Score: {r2:.3f}")

# Guardar modelo y scaler
joblib.dump(stack, MODEL_FILE)
joblib.dump(scaler, SCALER_FILE)

print("✅ Modelo guardado en:", MODEL_FILE)
