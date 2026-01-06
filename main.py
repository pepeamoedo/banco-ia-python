from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <--- IMPORTANTE

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
