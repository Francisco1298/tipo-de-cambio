# base_de_datos.py
# Paso 1: Crear la base de datos y la tabla

import sqlite3

# --- CONECTAR O CREAR LA BASE DE DATOS ---
# Si el archivo no existe, SQLite lo crea automáticamente
conexion = sqlite3.connect("tipos_de_cambio.db")
cursor = conexion.cursor()

print("✓ Base de datos conectada\n")

# --- CREAR LA TABLA ---
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tipos_de_cambio (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_consulta   TEXT NOT NULL,
        hora_consulta    TEXT NOT NULL,
        fecha_api        TEXT NOT NULL,
        moneda_base      TEXT NOT NULL,
        moneda_destino   TEXT NOT NULL,
        tipo_de_cambio   REAL NOT NULL,
        fuente           TEXT NOT NULL
    )
""")

conexion.commit()
print("✓ Tabla creada correctamente\n")

# --- VER LA ESTRUCTURA DE LA TABLA ---
cursor.execute("PRAGMA table_info(tipos_de_cambio)")
columnas = cursor.fetchall()

print("Estructura de la tabla:")
print(f"{'ID':<5} {'COLUMNA':<20} {'TIPO':<10} {'REQUERIDO'}")
print("-" * 45)
for columna in columnas:
    requerido = "Sí" if columna[3] else "No"
    print(f"{columna[0]:<5} {columna[1]:<20} {columna[2]:<10} {requerido}")

conexion.close()
print("\n✓ Proceso completado")