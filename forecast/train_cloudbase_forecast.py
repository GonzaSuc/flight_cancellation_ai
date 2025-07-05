# forecast/train_cloudbase_forecast.py

import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
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

OPENMETEO_FILE = "data/processed/cleaned_openmeteo_data.csv"
MODEL_FILE = "forecast/models/stacked_cloudbase_model.pkl"
SCALER_FILE = "forecast/models/cloudbase_scaler.pkl"
os.makedirs(os.path.dirname(MODEL_FILE), exist_ok=True)

df = pd.read_csv(OPENMETEO_FILE)
df['datetime'] = pd.to_datetime(df['datetime'])
df.sort_values(by=['station', 'datetime'], inplace=True)

df['cloudbase_t+1'] = df.groupby('station')['cloudcover'].shift(-1)
df.dropna(subset=['cloudbase_t+1'], inplace=True)

features = ['temperature_2m', 'dew_point_2m', 'cloudcover',
            'windspeed_10m', 'windgusts_10m', 'precipitation', 'pressure_msl']
df.dropna(subset=features, inplace=True)

X = df[features]
y = df['cloudbase_t+1']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

base_models = [
    ('rf', RandomForestRegressor(n_estimators=100, random_state=42)),
    ('gb', GradientBoostingRegressor(n_estimators=100, random_state=42)),
    ('knn', KNeighborsRegressor(n_neighbors=5)),
    ('svr', SVR()),
    ('mlp', MLPRegressor(max_iter=500, random_state=42))
]

meta_model = Ridge()

stack = StackingRegressor(
    estimators=base_models,
    final_estimator=meta_model,
    cv=5,
    n_jobs=-1
)

stack.fit(X_train, y_train)

# Evaluación
y_pred = stack.predict(X_test)
rmse = sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("📊 Cloud Base Forecast - Stacking Model")
print(f"✅ RMSE: {rmse:.2f}")
print(f"✅ R² Score: {r2:.3f}")

# Gráfico de dispersión
plt.figure(figsize=(6, 6))
plt.scatter(y_test, y_pred, alpha=0.3)
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
plt.xlabel("Actual Cloud Base")
plt.ylabel("Predicted Cloud Base")
plt.title("Actual vs Predicted Cloud Base")
plt.grid(True)
plt.tight_layout()
plt.show()

joblib.dump(stack, MODEL_FILE)
joblib.dump(scaler, SCALER_FILE)
print(f"✅ Model saved to: {MODEL_FILE}")
