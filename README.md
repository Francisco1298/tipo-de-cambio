# Pipeline de Tipos de Cambio con IA

Automatización completa que consulta tipos de cambio en tiempo real,
los almacena en Google Sheets y SQLite, y permite consultarlos
mediante un agente de inteligencia artificial en lenguaje natural.

## ¿Qué hace este proyecto?

- Consulta la API de Frankfurter (Banco Central Europeo) diariamente
- Transforma y limpia los datos (ETL)
- Guarda el histórico en Google Sheets y SQLite
- Expone un endpoint en la nube con Flask
- Se ejecuta automáticamente cada día con Make
- Permite hacer preguntas en lenguaje natural con un agente de IA

## Archivos

| Archivo | Descripción |
|---|---|
| `consulta.py` | ETL: API → Google Sheets |
| `consulta_sql.py` | ETL: API → SQLite |
| `app.py` | API propia con Flask (deploy en PythonAnywhere) |
| `agente.py` | Agente IA conectado a Google Sheets |
| `agente_sql.py` | Agente IA conectado a SQLite con SQL |
| `base_de_datos.py` | Creación de la base de datos |

## Stack tecnológico

- **Python 3.12** — lenguaje principal
- **requests** — consumo de API REST
- **gspread** — integración con Google Sheets
- **sqlite3** — base de datos local
- **Flask** — servidor web y endpoint propio
- **Groq + LLaMA 3.3** — agente de IA con function calling
- **Make** — automatización del flujo diario
- **PythonAnywhere** — deploy en la nube
- **Git + GitHub** — control de versiones

## Configuración

1. Clona el repositorio:
```bash
git clone https://github.com/Francisco1298/tipo-de-cambio.git
cd tipo-de-cambio
```

2. Instala las dependencias:
```bash
pip install requests gspread google-auth flask groq python-dotenv
```

3. Crea un archivo `.env` con tus credenciales: 
    GROQ_API_KEY=tu_api_key_de_groq
4. Agrega tu archivo `credenciales.json` de Google Cloud

5. Ejecuta el ETL:
```bash
python consulta_sql.py
```

6. Inicia el agente:
```bash
python agente_sql.py
```

## Ejemplo de uso del agente
Tú: ¿Cuánto vale el euro hoy?
Agente: El euro vale 0.85193 respecto al dólar estadounidense.
Tú: ¿Cuál es la moneda más débil?
Agente: La moneda más débil es el yen japonés (JPY) con 157.59 yenes por dólar.
Tú: ¿Cuántos pesos mexicanos necesito para comprar 50 euros?
Agente: Necesitarías aproximadamente 1012.35 pesos mexicanos.

## Conceptos aplicados

- ETL (Extract, Transform, Load)
- Consumo de APIs REST
- Function Calling con LLMs
- Agentes de IA
- Deploy en la nube
- Automatización con iPaaS
- SQL básico e intermedio
- Variables de entorno y seguridad