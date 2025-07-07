import tkinter as tk
from tkinter import ttk
import pandas as pd

# Archivos actualizados
estado_file = "data/processed/estado_vuelos.csv"
visibilidad_file = "forecast/output/visibility_forecast.csv"
cloudbase_file = "forecast/output/cloudbase_forecast.csv"
alertas_file = "forecast/alerts.csv"

# Crear ventana
ventana = tk.Tk()
ventana.title("Estado de Vuelos por Clima")
ventana.geometry("500x300")
ventana.configure(bg="#f0f0f0")

# Etiqueta de título
titulo = tk.Label(ventana, text="🛬 Estado Actual de Vuelos", font=("Helvetica", 16, "bold"), bg="#f0f0f0")
titulo.pack(pady=10)

# Lista de aeropuertos disponibles
aeropuertos = ['SPQU', 'SPRU', 'SPZO', 'SPJR', 'SPHZ']

# Combobox para seleccionar aeropuerto
combo = ttk.Combobox(ventana, values=aeropuertos, state="readonly", font=("Helvetica", 12))
combo.set("Selecciona un aeropuerto")
combo.pack(pady=10)

# Etiquetas de salida
label_estado = tk.Label(ventana, text="", font=("Helvetica", 12), bg="#f0f0f0")
label_vis = tk.Label(ventana, text="", font=("Helvetica", 12), bg="#f0f0f0")
label_cld = tk.Label(ventana, text="", font=("Helvetica", 12), bg="#f0f0f0")
label_alerta = tk.Label(ventana, text="", font=("Helvetica", 12, "bold"), fg="red", bg="#f0f0f0")

label_estado.pack(pady=2)
label_vis.pack(pady=2)
label_cld.pack(pady=2)
label_alerta.pack(pady=5)

# Función principal
def mostrar_info():
    aeropuerto = combo.get()

    # Leer archivos
    estado_df = pd.read_csv(estado_file)
    vis_df = pd.read_csv(visibilidad_file)
    cld_df = pd.read_csv(cloudbase_file)
    alert_df = pd.read_csv(alertas_file)

    # Obtener últimos registros por aeropuerto
    estado = estado_df[estado_df["station"] == aeropuerto].iloc[-1]["estado_vuelo"]
    vis = vis_df[vis_df["station"] == aeropuerto].iloc[-1]["predicted_visibility_t+1"]
    cld_m = cld_df[cld_df["station"] == aeropuerto].iloc[-1]["predicted_clouds_t+1"]
    cld_ft = cld_m * 3.28084  # convertir a pies

    # Intentar leer alerta si existe
    try:
        alerta = alert_df[alert_df["station"] == aeropuerto].iloc[-1]["alerta"]
    except:
        alerta = "Sin alerta generada"

    # Mostrar en etiquetas
    label_estado.config(text=f"Estado actual: {estado}")
    label_vis.config(text=f"Visibilidad +1h: {int(vis)} m")
    label_cld.config(text=f"Techo de nubes +1h: {int(cld_ft)} ft")
    label_alerta.config(text=f"🚨 Alerta: {alerta}")

# Botón de acción
boton = tk.Button(ventana, text="Consultar estado", command=mostrar_info, font=("Helvetica", 12), bg="#4CAF50", fg="white")
boton.pack(pady=10)

# Ejecutar interfaz
ventana.mainloop()
