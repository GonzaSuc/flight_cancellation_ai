# forecast/train_forecast_model.py

import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, StackingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from math import sqrt
import joblib
import matplotlib.pyplot as plt

# Archivos de entrada y salida
FILE = "data/processed/cleaned_weather_data.csv"
MODEL_FILE = "forecast/models/stacked_visibility_model.pkl"
SCALER_FILE = "forecast/models/visibility_scaler.pkl"
os.makedirs(os.path.dirname(MODEL_FILE), exist_ok=True)

# Cargar datos
df = pd.read_csv(FILE)
df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
df = df.sort_values(by=['station', 'datetime'])

# Convertir wind_dir: 'VRB' -> 0 y asegurar tipo numérico
df['wind_dir'] = df['wind_dir'].replace('VRB', 0)
df['wind_dir'] = pd.to_numeric(df['wind_dir'], errors='coerce')
df['wind_speed'] = pd.to_numeric(df['wind_speed'], errors='coerce')
df['visibility'] = pd.to_numeric(df['visibility'], errors='coerce')

# Crear columna de visibilidad futura
df['visibility_t+1'] = df.groupby('station')['visibility'].shift(-1)

# Eliminar valores nulos
df.dropna(subset=['wind_dir', 'wind_speed', 'visibility', 'visibility_t+1'], inplace=True)

# Features y target
features = ['wind_dir', 'wind_speed', 'visibility']
X = df[features]
y = df['visibility_t+1']

# Escalado
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# División train/test
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Modelos base
base_models = [
    ('rf', RandomForestRegressor(n_estimators=100, random_state=42)),
    ('gb', GradientBoostingRegressor(n_estimators=100, random_state=42)),
    ('knn', KNeighborsRegressor(n_neighbors=5)),
    ('svr', SVR()),
    ('mlp', MLPRegressor(max_iter=500, random_state=42))
]

# Meta-modelo
meta_model = Ridge()

# Stacking Regressor
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
cv_r2 = cross_val_score(stack, X_scaled, y, cv=5, scoring='r2').mean()

print("📊 Visibility Forecast - Stacking Model")
print(f"✅ RMSE: {rmse:.4f}")
print(f"✅ R² Score: {r2:.4f}")
print(f"✅ Cross-validated R² Score: {cv_r2:.4f}")

# Guardar modelo y scaler
joblib.dump(stack, MODEL_FILE)
joblib.dump(scaler, SCALER_FILE)
print(f"✅ Model saved to: {MODEL_FILE}")

# Diagrama de dispersión
plt.figure(figsize=(6, 6))
plt.scatter(y_test, y_pred, alpha=0.4, edgecolor='k')
plt.plot([y.min(), y.max()], [y.min(), y.max()], '--r', linewidth=2)
plt.xlabel("Actual Visibility (t+1)")
plt.ylabel("Predicted Visibility (t+1)")
plt.title("Scatter Plot: Actual vs Predicted Visibility")
plt.grid(True)
plt.tight_layout()
plt.show()
