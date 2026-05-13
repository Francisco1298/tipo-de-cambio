# agente.py
# Paso 3: Agente completo con conversación real

import json
import gspread
from groq import Groq
from google.oauth2.service_account import Credentials

# --- CONFIGURACIÓN ---
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
ARCHIVO_CREDENCIALES = "credenciales.json"
NOMBRE_HOJA = "Tipos de Cambio"

# --- CONECTAR CON GOOGLE SHEETS ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
credenciales = Credentials.from_service_account_file(
    ARCHIVO_CREDENCIALES, scopes=SCOPES
)
cliente_sheets = gspread.authorize(credenciales)
hoja = cliente_sheets.open(NOMBRE_HOJA).sheet1

# --- HERRAMIENTA 1: tipo de cambio más reciente ---
def buscar_tipo_de_cambio(moneda):
    registros = hoja.get_all_records()
    filtrados = [r for r in registros if r["moneda_destino"] == moneda.upper()]

    if not filtrados:
        return f"No encontré registros para {moneda.upper()}"

    ultimo = filtrados[-1]
    return (
        f"USD/{moneda.upper()}: {ultimo['tipo_de_cambio']} "
        f"(fecha: {ultimo['fecha_consulta']}, hora: {ultimo['hora_consulta']})"
    )

# --- HERRAMIENTA 2: listar todas las monedas disponibles ---
def listar_monedas():
    registros = hoja.get_all_records()
    monedas = list(set(r["moneda_destino"] for r in registros))
    return f"Monedas disponibles: {', '.join(sorted(monedas))}"

# --- HERRAMIENTA 3: comparar dos monedas ---
def comparar_monedas(moneda1, moneda2):
    registros = hoja.get_all_records()

    def ultimo_valor(moneda):
        filtrados = [r for r in registros if r["moneda_destino"] == moneda.upper()]
        return filtrados[-1]["tipo_de_cambio"] if filtrados else None

    valor1 = ultimo_valor(moneda1)
    valor2 = ultimo_valor(moneda2)

    if not valor1 or not valor2:
        return "No encontré datos para una o ambas monedas"

    return (
        f"USD/{moneda1.upper()}: {valor1} | "
        f"USD/{moneda2.upper()}: {valor2}"
    )

# --- DEFINIR HERRAMIENTAS PARA EL MODELO ---
herramientas = [
    {
        "type": "function",
        "function": {
            "name": "buscar_tipo_de_cambio",
            "description": "Busca el tipo de cambio más reciente de una moneda",
            "parameters": {
                "type": "object",
                "properties": {
                    "moneda": {
                        "type": "string",
                        "description": "Código de la moneda: EUR, MXN, BRL, GBP, JPY"
                    }
                },
                "required": ["moneda"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "listar_monedas",
            "description": "Lista todas las monedas disponibles en los registros",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "comparar_monedas",
            "description": "Compara el tipo de cambio entre dos monedas",
            "parameters": {
                "type": "object",
                "properties": {
                    "moneda1": {
                        "type": "string",
                        "description": "Primera moneda: EUR, MXN, BRL, GBP, JPY"
                    },
                    "moneda2": {
                        "type": "string",
                        "description": "Segunda moneda: EUR, MXN, BRL, GBP, JPY"
                    }
                },
                "required": ["moneda1", "moneda2"]
            }
        }
    }
]

# --- EJECUTAR HERRAMIENTA ---
def ejecutar_herramienta(nombre, argumentos):
    if nombre == "buscar_tipo_de_cambio":
        return buscar_tipo_de_cambio(argumentos["moneda"])
    elif nombre == "listar_monedas":
        return listar_monedas()
    elif nombre == "comparar_monedas":
        return comparar_monedas(argumentos["moneda1"], argumentos["moneda2"])
    else:
        return "Herramienta no encontrada"

# --- AGENTE PRINCIPAL ---
cliente_groq = Groq(api_key=API_KEY)

messages = [
    {
        "role": "system",
        "content": (
            "Eres un asistente experto en tipos de cambio. "
            "Tienes acceso a registros históricos reales en Google Sheets. "
            "Siempre usa las herramientas para responder con datos reales. "
            "Responde siempre en español de forma clara y concisa."
        )
    }
]

print("=" * 50)
print("Agente de Tipos de Cambio")
print("Puedes preguntar cosas como:")
print("  - ¿Cuánto vale el euro hoy?")
print("  - ¿Qué monedas tienes disponibles?")
print("  - Compara el yen japonés con el peso mexicano")
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

    # mantener solo el system prompt y los últimos 6 mensajes
    if len(messages) > 7:
        messages = [messages[0]] + messages[-6:]

    # llamada al modelo
    respuesta = cliente_groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        tools=herramientas,
        tool_choice="auto"
    )

    mensaje = respuesta.choices[0].message

    # si el modelo quiere usar una herramienta
    if mensaje.tool_calls:
        messages.append({"role": "assistant", "tool_calls": mensaje.tool_calls})

        for tool_call in mensaje.tool_calls:
            nombre = tool_call.function.name
            argumentos = json.loads(tool_call.function.arguments)
            resultado = ejecutar_herramienta(nombre, argumentos)
            print(f"[buscando {nombre}...]")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": resultado
            })

        # respuesta final con los datos reales
        respuesta_final = cliente_groq.chat.completions.create(
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