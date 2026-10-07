import uvicorn
from fastapi import FastAPI, APIRouter

app = FastAPI()

router = APIRouter(prefix="/contas-a-pagar-e-receber")

@router.get("/contas")
def listarContas():
    return [
        {"Conta 1": "Contas 1"},
        {"Conta 2": "Contas 2"},
        {"Conta 3": "Contas 3"}
    ]



