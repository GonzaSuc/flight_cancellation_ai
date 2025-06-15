import tkinter as tk
from tkinter import ttk
import pandas as pd

# Cargar archivos
estado_file = "data/processed/estado_vuelos.csv"
visibilidad_file = "forecast/predicted_visibility.csv"
cloudbase_file = "forecast/predicted_cloudbase.csv"
alertas_file = "forecast/alerts.csv"

# Cargar data
estado_df = pd.read_csv(estado_file)
vis_df = pd.read_csv(visibilidad_file)
cld_df = pd.read_csv(cloudbase_file)
alert_df = pd.read_csv(alertas_file)

# Lista única de aeropuertos
aeropuertos = sorted(estado_df["station"].unique())

# Función para mostrar info
def mostrar_info():
    aeropuerto = combo.get()

    estado = estado_df[estado_df["station"] == aeropuerto].iloc[-1]["estado_vuelo"]
    vis = vis_df[vis_df["station"] == aeropuerto].iloc[-1]["predicted_visibility_next_hour"]
    cld_m = cld_df[cld_df["station"] == aeropuerto].iloc[-1]["cloudbase_t+1"]
    cld_ft = cld_m * 3.28084  # convertir metros a pies

    try:
        alerta = alert_df[alert_df["station"] == aeropuerto].iloc[-1]["alerta"]
    except:
        alerta = "Sin alerta generada"

    label_estado.config(text=f"Estado actual: {estado}")
    label_vis.config(text=f"Visibilidad +1h: {int(vis)} m")
    label_cld.config(text=f"Techo de nubes +1h: {int(cld_ft)} ft")
    label_alerta.config(text=f"🚨 Alerta: {alerta}")

# Interfaz
ventana = tk.Tk()
ventana.title("Predicción y Alertas de Vuelo")
ventana.geometry("450x300")

tk.Label(ventana, text="Selecciona un aeropuerto:").pack(pady=10)

combo = ttk.Combobox(ventana, values=aeropuertos)
combo.pack()

tk.Button(ventana, text="Mostrar información", command=mostrar_info).pack(pady=10)

label_estado = tk.Label(ventana, text="", font=("Arial", 12))
label_estado.pack()

label_vis = tk.Label(ventana, text="", font=("Arial", 12))
label_vis.pack()

label_cld = tk.Label(ventana, text="", font=("Arial", 12))
label_cld.pack()

label_alerta = tk.Label(ventana, text="", font=("Arial", 12), fg="red")
label_alerta.pack(pady=10)

ventana.mainloop()
