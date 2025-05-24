import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import os

def load_and_clean_excel(filepath):
    # Leer Excel
    df = pd.read_excel(filepath, engine='openpyxl')

    print("Primeras filas del archivo original:")
    print(df.head())

    # Eliminar columnas irrelevantes si las hay
    columnas_a_eliminar = ['Estación', 'Código', 'Departamento']  # cambia según tu archivo
    df = df.drop(columns=[col for col in columnas_a_eliminar if col in df.columns], errors='ignore')

    # Renombrar columnas (ajusta los nombres reales del Excel)
    df = df.rename(columns={
        'Temp (°C)': 'temperature',
        'Humedad (%)': 'humidity',
        'Vel viento (km/h)': 'wind_speed',
        'Presión (hPa)': 'pressure',
        'Visibilidad (km)': 'visibility',
        'Precipitación (mm)': 'precipitation',
        'Cancelado': 'cancellation'  # si existe
    })

    # Eliminar filas con valores faltantes
    df = df.dropna()

    # Convertir a numérico
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna()

    print("\nColumnas después de limpieza:")
    print(df.columns)

    # Normalizar (excepto la variable objetivo)
    scaler = MinMaxScaler()
    features = df.drop('cancellation', axis=1)
    scaled_features = scaler.fit_transform(features)
    df_scaled = pd.DataFrame(scaled_features, columns=features.columns)
    df_scaled['cancellation'] = df['cancellation'].values

    # Guardar CSV
    os.makedirs('data/processed', exist_ok=True)
    df_scaled.to_csv('data/processed/clean_data.csv', index=False)
    print("\n✅ Datos limpios guardados en: data/processed/clean_data.csv")

# Ejecutar como script
if __name__ == "__main__":
    ruta_excel = "data/raw/tu_archivo_senamhi.xlsx"  # actualiza este nombre
    load_and_clean_excel(ruta_excel)
