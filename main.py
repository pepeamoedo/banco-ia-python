import sqlite3 # <--- 1. Importamos la herramienta de base de datos
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuración de CORS (Igual que antes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Transferencia(BaseModel):
    origen: str
    destino: str
    cantidad: float

# --- 2. CONFIGURACIÓN DE LA BASE DE DATOS ---
def init_db():
    """Crea la tabla y mete datos iniciales si está vacía"""
    conn = sqlite3.connect("banco.db") # Crea el archivo si no existe
    c = conn.cursor()
    # Creamos la tabla 'usuarios' con columnas 'nombre' y 'saldo'
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                 (nombre text PRIMARY KEY, saldo real)''')
    
    # Verificamos si hay datos. Si no, metemos los de prueba
    c.execute("SELECT count(*) FROM usuarios")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO usuarios VALUES ('pepe', 1500)")
        c.execute("INSERT INTO usuarios VALUES ('maria', 3000)")
        c.execute("INSERT INTO usuarios VALUES ('juan', 50)")
        conn.commit() # Guardamos los cambios
        print("Base de datos inicializada con datos de prueba.")
    
    conn.close()

# Ejecutamos esto AL ARRANCAR la aplicación
init_db()

# --- 3. NUEVAS FUNCIONES DE ENDPOINTS (CON SQL) ---

@app.get("/saldo/{usuario}")
def obtener_saldo(usuario: str):
    conn = sqlite3.connect("banco.db")
    c = conn.cursor()
    
    # Buscamos en el archivo
    c.execute("SELECT saldo FROM usuarios WHERE nombre = ?", (usuario.lower(),))
    resultado = c.fetchone() # Trae la primera coincidencia
    conn.close()

    if resultado:
        return {"usuario": usuario, "saldo_actual": resultado[0], "moneda": "EUR"}
    else:
        # Si el usuario no existe en la DB, devolvemos 0
        return {"usuario": usuario, "saldo_actual": 0, "moneda": "EUR"}

@app.get("/consejo/{usuario}")
def dar_consejo_ia(usuario: str):
    # Reutilizamos la lógica de obtener saldo, pero leyendo de la DB
    conn = sqlite3.connect("banco.db")
    c = conn.cursor()
    c.execute("SELECT saldo FROM usuarios WHERE nombre = ?", (usuario.lower(),))
    resultado = c.fetchone()
    conn.close()

    saldo = resultado[0] if resultado else 0
    
    # Lógica de IA (Igual que antes)
    consejo = ""
    if saldo < 0:
        consejo = "🚨 ALERTA ROJA: Estás en números rojos."
    elif saldo < 100:
        consejo = "⚠️ Precaución: Tienes muy poco margen."
    elif saldo < 2000:
        consejo = "✅ Vas bien: Tienes un colchón de seguridad."
    else:
        consejo = "🚀 Magnífico estado financiero: Deberías invertir."

    return {"usuario": usuario, "analisis": "Financiero-SQL v2", "consejo": consejo}

@app.post("/transferir")
def realizar_transferencia(transaccion: Transferencia):
    origen = transaccion.origen.lower()
    destino = transaccion.destino.lower()
    
    conn = sqlite3.connect("banco.db")
    c = conn.cursor()
    
    try:
        # 1. Comprobar saldo del origen
        c.execute("SELECT saldo FROM usuarios WHERE nombre = ?", (origen,))
        res_origen = c.fetchone()
        
        if not res_origen:
            raise HTTPException(status_code=404, detail="Usuario origen no existe")
        
        saldo_origen = res_origen[0]
        
        # 2. Comprobar que existe el destino
        c.execute("SELECT saldo FROM usuarios WHERE nombre = ?", (destino,))
        if not c.fetchone():
            raise HTTPException(status_code=404, detail="Usuario destino no existe")

        # 3. Validar fondos
        if saldo_origen < transaccion.cantidad:
            raise HTTPException(status_code=400, detail="Fondos insuficientes")

        # 4. EJECUTAR LA TRANSACCIÓN (SQL UPDATE)
        # Restar al origen
        c.execute("UPDATE usuarios SET saldo = saldo - ? WHERE nombre = ?", (transaccion.cantidad, origen))
        # Sumar al destino
        c.execute("UPDATE usuarios SET saldo = saldo + ? WHERE nombre = ?", (transaccion.cantidad, destino))
        
        conn.commit() # <--- IMPORTANTE: Guardar cambios en el disco

        # Obtener nuevos saldos para confirmar
        c.execute("SELECT saldo FROM usuarios WHERE nombre = ?", (origen,))
        nuevo_origen = c.fetchone()[0]
        c.execute("SELECT saldo FROM usuarios WHERE nombre = ?", (destino,))
        nuevo_destino = c.fetchone()[0]
        
        return {
            "mensaje": "Transferencia exitosa",
            "saldo_origen_nuevo": nuevo_origen,
            "saldo_destino_nuevo": nuevo_destino
        }
        
    except Exception as e:
        conn.rollback() # Si algo falla, deshacer cambios
        raise e
    finally:
        conn.close() # Cerrar conexión siempre

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
