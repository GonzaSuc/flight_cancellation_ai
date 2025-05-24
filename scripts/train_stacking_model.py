# scripts/train_stacking_model.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
import matplotlib.pyplot as plt
import seaborn as sns

# Leer datos
df = pd.read_csv("data/processed/estado_vuelos.csv")

# Filtrar solo los estados válidos para clasificación
df = df[df['estado_vuelo'].isin([
    "✅ Operativo",
    "⏳ En espera (condiciones bajo mínimo)",
    "❌ Cancelado por mal clima"
])]

# Limpiar nulos y rellenar columnas vacías
df.fillna({'clouds': '', 'phenomena': '', 'intensity_prefix': ''}, inplace=True)
df.dropna(subset=['wind_dir', 'wind_speed', 'visibility'], inplace=True)

# Convertir tipos
df['wind_dir'] = pd.to_numeric(df['wind_dir'], errors='coerce')
df['wind_speed'] = pd.to_numeric(df['wind_speed'], errors='coerce')
df['visibility'] = pd.to_numeric(df['visibility'], errors='coerce')
df.dropna(subset=['wind_dir', 'wind_speed', 'visibility'], inplace=True)

# Codificación categórica
le_station = LabelEncoder()
le_clouds = LabelEncoder()
le_phenomena = LabelEncoder()
le_prefix = LabelEncoder()
le_estado = LabelEncoder()

df['station'] = le_station.fit_transform(df['station'])
df['clouds'] = le_clouds.fit_transform(df['clouds'])
df['phenomena'] = le_phenomena.fit_transform(df['phenomena'])
df['intensity_prefix'] = le_prefix.fit_transform(df['intensity_prefix'])
df['estado_vuelo'] = le_estado.fit_transform(df['estado_vuelo'])

# Features y target
features = ['station', 'wind_dir', 'wind_speed', 'visibility', 'clouds', 'phenomena', 'intensity_prefix']
X = df[features]
y = df['estado_vuelo']

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.25, random_state=42)

# Modelos base
estimators = [
    ('rf', RandomForestClassifier(n_estimators=100, random_state=42)),
    ('gb', GradientBoostingClassifier(n_estimators=100, random_state=42)),
    ('knn', KNeighborsClassifier(n_neighbors=5)),
    ('lr', LogisticRegression(max_iter=1000))
]

# Meta-modelo
stack_model = StackingClassifier(
    estimators=estimators,
    final_estimator=XGBClassifier(use_label_encoder=False, eval_metric='mlogloss'),
    cv=5,
    n_jobs=-1
)

# Entrenamiento
stack_model.fit(X_train, y_train)

# Evaluación
y_pred = stack_model.predict(X_test)

print("📊 Classification Report:\n")
print(classification_report(y_test, y_pred, target_names=le_estado.classes_))

# Matriz de confusión
conf_mat = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6, 5))
sns.heatmap(conf_mat, annot=True, fmt='d', cmap='Blues', xticklabels=le_estado.classes_, yticklabels=le_estado.classes_)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix - Stacking Classifier")
plt.tight_layout()
plt.show()
