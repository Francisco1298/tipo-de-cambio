# agente_sql.py
# Paso 3: Agente que consulta la base de datos con SQL

import json
import sqlite3
from groq import Groq

# --- CONFIGURACIÓN ---
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
BASE_DE_DATOS = "tipos_de_cambio.db"

# --- FUNCIÓN PARA EJECUTAR SQL ---
def ejecutar_sql(consulta):
    """
    Ejecuta una consulta SQL y devuelve los resultados
    """
    try:
        conexion = sqlite3.connect(BASE_DE_DATOS)
        cursor = conexion.cursor()
        cursor.execute(consulta)
        resultados = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]
        conexion.close()

        if not resultados:
            return "No se encontraron resultados"

        # formatear resultados como texto legible
        texto = []
        for fila in resultados:
            fila_texto = " | ".join(f"{columnas[i]}: {fila[i]}" for i in range(len(fila)))
            texto.append(fila_texto)

        return "\n".join(texto)

    except Exception as e:
        return f"Error en la consulta: {str(e)}"

# --- HERRAMIENTA: consultar base de datos ---
herramientas = [
    {
        "type": "function",
        "function": {
            "name": "ejecutar_sql",
            "description": """Ejecuta consultas SQL sobre la base de datos de tipos de cambio.
            La tabla se llama 'tipos_de_cambio' y tiene estas columnas:
            - id: número único de registro
            - fecha_consulta: fecha en que se registró (TEXT, formato YYYY-MM-DD)
            - hora_consulta: hora en que se registró (TEXT, formato HH:MM:SS)
            - fecha_api: fecha oficial del tipo de cambio (TEXT)
            - moneda_base: siempre USD (TEXT)
            - moneda_destino: EUR, MXN, BRL, GBP, JPY (TEXT)
            - tipo_de_cambio: valor numérico (REAL)
            - fuente: origen del dato (TEXT)
            Solo usa SELECT, nunca INSERT, UPDATE ni DELETE.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "consulta": {
                        "type": "string",
                        "description": "La consulta SQL a ejecutar"
                    }
                },
                "required": ["consulta"]
            }
        }
    }
]

# --- AGENTE PRINCIPAL ---
cliente = Groq(api_key=API_KEY)

messages = [
    {
        "role": "system",
        "content": """Eres un asistente experto en tipos de cambio.
        Tienes acceso a una base de datos SQLite con histórico de tipos de cambio.
        Cuando necesites datos, genera la consulta SQL correcta y úsala.
        Responde siempre en español de forma clara y concisa.
        Nunca uses INSERT, UPDATE ni DELETE — solo SELECT.

        REGLA IMPORTANTE sobre tipos de cambio:
        La tabla almacena cuántas unidades de moneda_destino equivalen a 1 USD.
        - Valor alto = moneda débil (ej: JPY 157 = necesitas muchos yenes por 1 dólar)
        - Valor bajo = moneda fuerte (ej: GBP 0.73 = necesitas pocas libras por 1 dólar)
        Usa esta lógica siempre al interpretar los resultados."""
    }
]
print("=" * 50)
print("Agente SQL de Tipos de Cambio")
print("Puedes preguntar cosas como:")
print("  - ¿Cuánto vale el euro hoy?")
print("  - ¿Cuál es la moneda más débil?")
print("  - ¿Cuántos registros hay en la base de datos?")
print("  - ¿Cuál fue el tipo de cambio más alto del yen?")
print("  - Escribe 'salir' para terminar")
print("=" * 50)

# --- BUCLE DE CONVERSACIÓN ---
while True:
    try:
        pregunta = input("\nTú: ").strip()
    except EOFError:
        break

    if pregunta.lower() == "salir":
        print("Agente: ¡Hasta luego!")
        break

    if not pregunta:
        continue

    messages.append({"role": "user", "content": pregunta})

    if len(messages) > 7:
        messages = [messages[0]] + messages[-6:]

    respuesta = cliente.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        tools=herramientas,
        tool_choice="auto"
    )

    mensaje = respuesta.choices[0].message

    if mensaje.tool_calls:
        messages.append({"role": "assistant", "tool_calls": mensaje.tool_calls})

        for tool_call in mensaje.tool_calls:
            argumentos = json.loads(tool_call.function.arguments)
            consulta_sql = argumentos["consulta"]
            print(f"\n[SQL]: {consulta_sql}")
            resultado = ejecutar_sql(consulta_sql)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": resultado
            })

        respuesta_final = cliente.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=herramientas
        )

        respuesta_texto = respuesta_final.choices[0].message.content
        messages.append({"role": "assistant", "content": respuesta_texto})

    else:
        respuesta_texto = mensaje.content
        messages.append({"role": "assistant", "content": respuesta_texto})

    print(f"\nAgente: {respuesta_texto}")