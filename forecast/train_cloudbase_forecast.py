import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, StackingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from math import sqrt
import joblib

OPENMETEO_FILE = "data/processed/cleaned_openmeteo_data.csv"
CLOUDBASE_MODEL_FILE = "forecast/models/stacked_cloudbase_model.pkl"
SCALER_FILE = "forecast/models/cloudbase_scaler.pkl"

# Crear carpeta si no existe
os.makedirs("forecast/models", exist_ok=True)

# Cargar datos
df = pd.read_csv(OPENMETEO_FILE)
df['datetime'] = pd.to_datetime(df['datetime'])
df = df.sort_values(by=['station', 'datetime'])

# Crear columna objetivo: techo de nubes en la siguiente hora
df['cloudbase_t+1'] = df.groupby('station')['cloudcover'].shift(-1)

# Eliminar nulos generados por el shift
df.dropna(subset=['cloudbase_t+1'], inplace=True)

# Features relevantes
features = ['temperature_2m', 'dew_point_2m', 'cloudcover', 'windspeed_10m',
            'windgusts_10m', 'precipitation', 'pressure_msl']
X = df[features]
y = df['cloudbase_t+1']

# Escalamiento
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split
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

# Entrenamiento
stack.fit(X_train, y_train)

# Evaluación
y_pred = stack.predict(X_test)
rmse = sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("📊 Stacking Regressor para techo de nubes (+1h)")
print(f"✅ RMSE: {rmse:.2f}")
print(f"✅ R² Score: {r2:.3f}")

# Guardar modelo y scaler
joblib.dump(stack, CLOUDBASE_MODEL_FILE)
joblib.dump(scaler, SCALER_FILE)
print("✅ Modelo guardado en:", CLOUDBASE_MODEL_FILE)
