from decimal import Decimal
from typing import List

import uvicorn
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

app = FastAPI()

router = APIRouter(prefix="/contas-a-pagar-e-receber")


class ContaPagarReceberResponse(BaseModel):
    id: int
    description: str
    valor: Decimal
    tipo: str  # PAGAR, RECEBER

class ContaPagarReceberRequest(BaseModel):
    description: str
    valor: Decimal
    tipo: str  # PAGAR, RECEBER


@router.get("/contas", response_model=List[ContaPagarReceberResponse])
def listarContas():
    return [
        ContaPagarReceberResponse(
            id=1,
            description="aluguel",
            valor=705.00,
            tipo="PAGAR"
        ),
        ContaPagarReceberResponse(
            id=1,
            description="cartão",
            valor=870.98,
            tipo="PAGAR"
        )

    ]

@router.post("/new", response_model=ContaPagarReceberResponse, status_code=201)
def noca_conta(conta: ContaPagarReceberRequest):
    return ContaPagarReceberResponse(
        id=3,
        description="busao",
        valor=250,
        tipo="PAGAR"
    )
