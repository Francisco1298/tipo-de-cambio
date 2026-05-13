# consulta.py
# Paso 3: Consultar + transformar + escribir en Google Sheets

import requests
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials

# --- CONFIGURACIÓN ---
MONEDA_BASE = "USD"
MONEDAS_DESTINO = ["EUR", "MXN", "BRL", "GBP", "JPY"]
URL = f"https://api.frankfurter.app/latest?from={MONEDA_BASE}"

ARCHIVO_CREDENCIALES = "credenciales.json"
NOMBRE_HOJA = "Tipos de Cambio"

# --- CONECTAR CON GOOGLE SHEETS ---
print("Conectando con Google Sheets...")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credenciales = Credentials.from_service_account_file(
    ARCHIVO_CREDENCIALES,
    scopes=SCOPES
)

cliente = gspread.authorize(credenciales)
hoja = cliente.open(NOMBRE_HOJA).sheet1
print("✓ Conexión con Google Sheets exitosa\n")

# --- CONSULTAR LA API ---
print("Consultando la API...")
respuesta = requests.get(URL)

if respuesta.status_code != 200:
    print(f"✗ Error en la API: {respuesta.status_code}")
    exit()

datos = respuesta.json()
print("✓ Datos recibidos\n")

# --- TRANSFORMAR LOS DATOS ---
ahora = datetime.now()
fecha_consulta = ahora.strftime("%Y-%m-%d")
hora_consulta  = ahora.strftime("%H:%M:%S")
fecha_api      = datos["date"]

filas = []
for moneda in MONEDAS_DESTINO:
    if moneda in datos["rates"]:
        fila = [
            fecha_consulta,
            hora_consulta,
            fecha_api,
            MONEDA_BASE,
            moneda,
            float(datos["rates"][moneda]),
            "frankfurter.app"
        ]
        filas.append(fila)

# --- ESCRIBIR EN GOOGLE SHEETS ---
print("Escribiendo en Google Sheets...")

# Agregar cada fila al final de la hoja (no sobreescribe, acumula)
for fila in filas:
    hoja.append_row(fila)

print(f"✓ {len(filas)} filas escritas correctamente")

# --- MOSTRAR RESUMEN EN CONSOLA ---
print(f"\n{'FECHA':<12} {'HORA':<10} {'PAR':<10} {'TIPO DE CAMBIO':>15}")
print("-" * 50)
for fila in filas:
    par = f"{fila[3]}/{fila[4]}"
    print(f"{fila[0]:<12} {fila[1]:<10} {par:<10} {fila[5]:>15}")

print(f"\nTotal de registros: {len(filas)}")
print("✓ Proceso completado")