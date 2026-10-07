import uvicorn
from fastapi import FastAPI
from contas_a_pagar_e_receber.routers import contas_a_pagar_e_receber_router


app = FastAPI()


@app.get("/")
def hello_api() -> str:
    return "Olá, acabei de consumir minha primeira api em pyton!"

app.include_router(contas_a_pagar_e_receber_router.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)