from decimal import Decimal

from sqlmodel import Field, SQLModel

from app.models.conta import TipoConta


# Requests e responses
class ContaCreate(SQLModel):
    nome: str = Field(min_length=3, max_length=100)
    tipo: TipoConta = TipoConta.CORRENTE
    saldo: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=12, decimal_places=2)


class ContaPublic(SQLModel):
    id: int
    nome: str
    tipo: TipoConta
    saldo: Decimal
    ativa: bool


# Dados para ATUALIZAR (PATCH). Todos opcionais: o cliente manda só
# o que quer mudar. O saldo não está aqui de propósito: ele só muda
# por depósito e saque, para não ser editado "na mão".
class ContaUpdate(SQLModel):
    nome: str | None = Field(default=None, min_length=3, max_length=100)
    tipo: TipoConta | None = None
    ativa: bool | None = None


# Corpo das operações de depósito e saque. gt=0 recusa zero e valores
# negativos antes de chegar no service.
class MovimentacaoCreate(SQLModel):
    valor: Decimal = Field(gt=0, max_digits=12, decimal_places=2)