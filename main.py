from fastapi import FastAPI
from pydantic import BaseModel # <--- NUEVO
from fastapi.middleware.cors import CORSMiddleware # <--- IMPORTANTE

# Definimos la estructura de una transferencia
class Transferencia(BaseModel):
    origen: str
    destino: str
    cantidad: float

app = FastAPI()

# --- BLOQUE DE SEGURIDAD (CORS) ---
# Le decimos a la API: "Deja pasar a cualquiera (*)"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ----------------------------------

datos = {
    "pepe": 1500,
    "maria": 3000,
    "juan": 50
}

@app.get("/saldo/{usuario}")
def obtener_saldo(usuario: str):
    dinero = datos.get(usuario.lower(), 0) # .lower() para que no importe mayúsculas
    return {"usuario": usuario, "saldo_actual": dinero, "moneda": "EUR"}

@app.post("/transferir")
def realizar_transferencia(transaccion: Transferencia):
    # 1. Validaciones básicas
    usuario_origen = transaccion.origen.lower()
    usuario_destino = transaccion.destino.lower()

    if usuario_origen not in datos:
        raise HTTPException(status_code=404, detail="Usuario origen no existe")
    if usuario_destino not in datos:
        raise HTTPException(status_code=404, detail="Usuario destino no existe")
    if transaccion.cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser positiva")
    if datos[usuario_origen] < transaccion.cantidad:
        raise HTTPException(status_code=400, detail="Fondos insuficientes")

    # 2. Ejecución de la transferencia (El movimiento de dinero)
    datos[usuario_origen] -= transaccion.cantidad
    datos[usuario_destino] += transaccion.cantidad

    return {
        "mensaje": "Transferencia exitosa",
        "saldo_origen_nuevo": datos[usuario_origen],
        "saldo_destino_nuevo": datos[usuario_destino]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
