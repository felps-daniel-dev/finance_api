from decimal import Decimal
from sqlmodel import SQLModel, Field
from app.models.enuns import TipoConta


# SQLModel herdando esta tela ele define que vai ser uma tabela no banco
class Conta(SQLModel, table=True):
    # Chave primária gerada pelo banco
    id: None

    nome: str

    tipo: TipoConta


    saldo: Decimal

    ativa: bool