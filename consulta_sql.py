# consulta_sql.py
# Paso 2: Consultar la API y guardar en base de datos SQLite

import sqlite3
import requests
from datetime import datetime

# --- CONFIGURACIÓN ---
MONEDA_BASE = "USD"
MONEDAS_DESTINO = ["EUR", "MXN", "BRL", "GBP", "JPY"]
URL = f"https://api.frankfurter.app/latest?from={MONEDA_BASE}"
BASE_DE_DATOS = "tipos_de_cambio.db"

# --- CONSULTAR LA API ---
print("Consultando la API...")
respuesta = requests.get(URL)

if respuesta.status_code != 200:
    print(f"✗ Error: {respuesta.status_code}")
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
        fila = (
            fecha_consulta,
            hora_consulta,
            fecha_api,
            MONEDA_BASE,
            moneda,
            float(datos["rates"][moneda]),
            "frankfurter.app"
        )
        filas.append(fila)

# --- GUARDAR EN LA BASE DE DATOS ---
print("Guardando en la base de datos...")
conexion = sqlite3.connect(BASE_DE_DATOS)
cursor = conexion.cursor()

cursor.executemany("""
    INSERT INTO tipos_de_cambio
        (fecha_consulta, hora_consulta, fecha_api,
         moneda_base, moneda_destino, tipo_de_cambio, fuente)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", filas)

conexion.commit()

# --- VERIFICAR LO QUE SE GUARDÓ ---
cursor.execute("SELECT COUNT(*) FROM tipos_de_cambio")
total = cursor.fetchone()[0]

cursor.execute("""
    SELECT fecha_consulta, hora_consulta, moneda_destino, tipo_de_cambio
    FROM tipos_de_cambio
    ORDER BY id DESC
    LIMIT 5
""")
ultimos = cursor.fetchall()

conexion.close()

# --- MOSTRAR RESUMEN ---
print(f"✓ {len(filas)} registros guardados\n")
print(f"{'FECHA':<12} {'HORA':<10} {'MONEDA':<8} {'TIPO DE CAMBIO':>15}")
print("-" * 48)
for registro in ultimos:
    print(f"{registro[0]:<12} {registro[1]:<10} {registro[2]:<8} {registro[3]:>15}")

print(f"\nTotal de registros en la base de datos: {total}")
print("✓ Proceso completado")