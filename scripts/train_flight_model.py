import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Cargar archivo procesado
df = pd.read_csv("data/processed/estado_vuelos.csv")

# Filtrar solo filas etiquetadas válidas
df = df[df['estado_vuelo'].isin([
    "✅ Operativo", 
    "⏳ En espera (condiciones bajo mínimo)", 
    "❌ Cancelado por mal clima"
])]

# Usar solo columnas relevantes para AVWX/CORPAC
possible_features = ['wind_dir', 'wind_speed', 'visibility']
features = [col for col in possible_features if col in df.columns]

print("✅ Usando columnas para entrenamiento:", features)

# Preparar los datos
X = df[features].copy()
y = df['estado_vuelo']

# Convertir posibles strings a números
X = X.apply(pd.to_numeric, errors='coerce')

# Eliminar filas con valores faltantes
X = X.dropna()
y = y[X.index]

# Dividir dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Entrenar modelo
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predicciones y evaluación
y_pred = model.predict(X_test)
print("\n📊 Reporte de clasificación:")
print(classification_report(y_test, y_pred))

# Matriz de confusión
cm = confusion_matrix(y_test, y_pred, labels=model.classes_)
sns.heatmap(cm, annot=True, fmt='d', xticklabels=model.classes_, yticklabels=model.classes_, cmap='Blues')
plt.xlabel("Predicción")
plt.ylabel("Valor Real")
plt.title("Matriz de Confusión")
plt.show()

import matplotlib.pyplot as plt
from sklearn.metrics import classification_report

# Después de hacer:
# model.fit(X, y)
y_pred = model.predict(X)
report = classification_report(y, y_pred, output_dict=True)

# Tomar precisión por clase
labels = list(report.keys())[:-3]  # excluir 'accuracy', 'macro avg', etc.
precision = [report[label]['precision'] for label in labels]

# Graficar
plt.figure(figsize=(8,5))
plt.plot(labels, precision, marker='o', linestyle='-', color='blue')
plt.ylim(0, 1.1)
plt.title("Precisión por clase")
plt.xlabel("Clase")
plt.ylabel("Precisión")
plt.grid(True)
plt.tight_layout()
plt.show()


importances = model.feature_importances_
features = X.columns

plt.figure(figsize=(10, 5))
plt.bar(features, importances, color='teal')
plt.xticks(rotation=45)
plt.title("Importancia de las variables")
plt.ylabel("Peso en la decisión")
plt.tight_layout()
plt.show()
