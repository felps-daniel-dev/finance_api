from decimal import Decimal
from enum import Enum

from sqlmodel import Field, SQLModel

class TipoConta(str, Enum):
    CORRENTE = "corrente"
    POUPANCA = "poupanca"
    CARTEIRA = "carteira"
    CAIXA = "caixa"


#  SqlModel define que vai ser criado uma tabela com os atributos da classe
class Conta(SQLModel, table=True):
    # Chave primária. Começa como None porque quem gera o número é
    # o banco, depois do insert.
    id: int | None = Field(default=None, primary_key=True)

    # Nome da conta. unique=True impede duas contas com o mesmo nome
    # no nível do banco, e index=True acelera buscas por nome.
    nome: str = Field(max_length=100, unique=True, index=True)

    # Tipo da conta, restrito aos valores do Enum acima.
    tipo: TipoConta = Field(default=TipoConta.CORRENTE)

    # max_digits=12 e decimal_places=2: até 9.999.999.999,99.
    saldo: Decimal = Field(default=Decimal("0.00"), max_digits=12, decimal_places=2)

    # Exclusão lógica: em vez de apagar a conta, marcamos como inativa
    # para preservar o histórico.
    ativa: bool = Field(default=True)