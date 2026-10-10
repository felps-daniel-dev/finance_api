from decimal import Decimal

from sqlmodel import Session, select

from app.core.exceptions import (
    ContaComSaldoError,
    ContaInativaError,
    NomeDuplicadoError,
    SaldoInsuficienteError,
)
from app.models.conta import Conta
from app.schemas.conta import ContaCreate, ContaUpdate


# Função interna (o "_" indica uso interno deste arquivo).
# Procura uma conta pelo nome e devolve None se não existir.
# Reaproveitada em criar e atualizar para checar duplicidade.
def _buscar_por_nome(session: Session, nome: str) -> Conta | None:
    return session.exec(select(Conta).where(Conta.nome == nome)).first()


# Cria uma conta. Primeiro verifica se o nome já existe (regra de
# negócio). Depois converte o schema para o modelo da tabela com
# model_validate, salva (add + commit) e faz refresh para carregar o
# id que o banco gerou.
def criar(session: Session, dados: ContaCreate) -> Conta:
    if _buscar_por_nome(session, dados.nome):
        raise NomeDuplicadoError(f"Já existe uma conta chamada '{dados.nome}'.")

    conta = Conta.model_validate(dados)
    session.add(conta)
    session.commit()
    session.refresh(conta)
    return conta


# Lista contas com paginação. offset é quantas pular e limit é
# quantas trazer, evitando devolver milhares de linhas de uma vez.
# Com somente_ativas=True, adiciona um filtro WHERE ativa = true.
def listar(
    session: Session,
    offset: int = 0,
    limit: int = 100,
    somente_ativas: bool = False,
) -> list[Conta]:
    consulta = select(Conta)
    if somente_ativas:
        consulta = consulta.where(Conta.ativa == True)  # noqa: E712
    consulta = consulta.offset(offset).limit(limit)
    return list(session.exec(consulta).all())


# Busca pela chave primária. session.get é o jeito mais direto.
# Devolve None se não existir: quem decide responder 404 é a rota.
def buscar_por_id(session: Session, conta_id: int) -> Conta | None:
    return session.get(Conta, conta_id)


# Atualização parcial. model_dump(exclude_unset=True) devolve só os
# campos que o cliente realmente enviou (ignora os que vieram vazios).
# Se estiver trocando o nome, confere se o novo nome já é de outra
# conta. sqlmodel_update aplica os campos no objeto existente.
def atualizar(session: Session, conta: Conta, dados: ContaUpdate) -> Conta:
    campos = dados.model_dump(exclude_unset=True)

    novo_nome = campos.get("nome")
    if novo_nome and novo_nome != conta.nome and _buscar_por_nome(session, novo_nome):
        raise NomeDuplicadoError(f"Já existe uma conta chamada '{novo_nome}'.")

    conta.sqlmodel_update(campos)
    session.add(conta)
    session.commit()
    session.refresh(conta)
    return conta


# Soma o valor ao saldo. Não aceita conta inativa. A soma é
# Decimal com Decimal, então não há erro de arredondamento de float.
def depositar(session: Session, conta: Conta, valor: Decimal) -> Conta:
    if not conta.ativa:
        raise ContaInativaError("Não é possível depositar em conta inativa.")

    conta.saldo += valor
    session.add(conta)
    session.commit()
    session.refresh(conta)
    return conta


# Subtrai do saldo. Duas regras: a conta precisa estar ativa e o
# saldo não pode ficar negativo. A checagem vem ANTES de alterar
# qualquer coisa, para nunca salvar um estado inválido.
def sacar(session: Session, conta: Conta, valor: Decimal) -> Conta:
    if not conta.ativa:
        raise ContaInativaError("Não é possível sacar de conta inativa.")
    if valor > conta.saldo:
        raise SaldoInsuficienteError(
            f"Saldo insuficiente: disponível {conta.saldo}, solicitado {valor}."
        )

    conta.saldo -= valor
    session.add(conta)
    session.commit()
    session.refresh(conta)
    return conta


# Exclusão lógica: marca ativa=False em vez de apagar o registro.
# Só permite se o saldo for zero, para não "esconder" dinheiro numa
# conta desativada.
def desativar(session: Session, conta: Conta) -> Conta:
    if conta.saldo != 0:
        raise ContaComSaldoError("Zere o saldo da conta antes de desativá-la.")

    conta.ativa = False
    session.add(conta)
    session.commit()
    session.refresh(conta)
    return conta