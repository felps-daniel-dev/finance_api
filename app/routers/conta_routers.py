from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.core.exceptions import (
    ContaComSaldoError,
    ContaInativaError,
    NomeDuplicadoError,
    SaldoInsuficienteError,
)
from app.models.conta import Conta
from app.schemas.conta import (
    ContaCreate,
    ContaPublic,
    ContaUpdate,
    MovimentacaoCreate,
)
from app.services import conta_service

# O prefixo evita repetir "/contas" em cada rota. As tags agrupam as
# rotas na documentação automática (/docs).
router = APIRouter(prefix="/contas", tags=["contas"])


# Função interna usada por várias rotas: busca a conta e, se não
# existir, já interrompe com 404. Evita repetir o mesmo if em todo lugar.
def _obter_conta_ou_404(session: Session, conta_id: int) -> Conta:
    conta = conta_service.buscar_por_id(session, conta_id)
    if conta is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Conta não encontrada.")
    return conta


# POST /contas
# Recebe ContaCreate no corpo (o FastAPI valida sozinho) e devolve
# ContaPublic. response_model filtra o que sai. Nome duplicado vira
# 409 (Conflict) e sucesso devolve 201 (Created).
@router.post("/", response_model=ContaPublic, status_code=status.HTTP_201_CREATED)
def criar(dados: ContaCreate, session: Session = Depends(get_session)):
    try:
        return conta_service.criar(session, dados)
    except NomeDuplicadoError as erro:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(erro))


# GET /contas?offset=0&limit=100&somente_ativas=true
# Os parâmetros fora do caminho viram query params. Query(le=100)
# impede pedir mais de 100 de uma vez.
@router.get("/", response_model=list[ContaPublic])
def listar(
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    somente_ativas: bool = False,
    session: Session = Depends(get_session),
):
    return conta_service.listar(session, offset, limit, somente_ativas)


# GET /contas/{conta_id}
# {conta_id} no caminho vira o parâmetro da função, já convertido
# para int. Se não for número, o FastAPI responde 422 sozinho.
@router.get("/{conta_id}", response_model=ContaPublic)
def buscar(conta_id: int, session: Session = Depends(get_session)):
    return _obter_conta_ou_404(session, conta_id)


# PATCH /contas/{conta_id}
# Atualização parcial. Primeiro garante que a conta existe (404),
# depois atualiza. Trocar para um nome já usado devolve 409.
@router.patch("/{conta_id}", response_model=ContaPublic)
def atualizar(
    conta_id: int,
    dados: ContaUpdate,
    session: Session = Depends(get_session),
):
    conta = _obter_conta_ou_404(session, conta_id)
    try:
        return conta_service.atualizar(session, conta, dados)
    except NomeDuplicadoError as erro:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(erro))


# POST /contas/{conta_id}/depositar
# Rota de "ação": não é CRUD puro, é uma operação sobre a conta.
# Recebe o valor e devolve a conta com o saldo atualizado. Conta
# inativa devolve 409.
@router.post("/{conta_id}/depositar", response_model=ContaPublic)
def depositar(
    conta_id: int,
    dados: MovimentacaoCreate,
    session: Session = Depends(get_session),
):
    conta = _obter_conta_ou_404(session, conta_id)
    try:
        return conta_service.depositar(session, conta, dados.valor)
    except ContaInativaError as erro:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(erro))


# POST /contas/{conta_id}/sacar
# Mesma ideia do depósito, com dois erros possíveis: conta inativa
# (409, conflito de estado) e saldo insuficiente (422, o pedido é
# válido no formato, mas não pode ser processado).
@router.post("/{conta_id}/sacar", response_model=ContaPublic)
def sacar(
    conta_id: int,
    dados: MovimentacaoCreate,
    session: Session = Depends(get_session),
):
    conta = _obter_conta_ou_404(session, conta_id)
    try:
        return conta_service.sacar(session, conta, dados.valor)
    except ContaInativaError as erro:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(erro))
    except SaldoInsuficienteError as erro:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(erro))


# DELETE /contas/{conta_id}
# Faz exclusão lógica (desativa). Como o registro continua existindo,
# devolve a conta já desativada com 200 em vez de 204 (sem conteúdo).
# Conta com saldo diferente de zero devolve 409.
@router.delete("/{conta_id}", response_model=ContaPublic)
def desativar(conta_id: int, session: Session = Depends(get_session)):
    conta = _obter_conta_ou_404(session, conta_id)
    try:
        return conta_service.desativar(session, conta)
    except ContaComSaldoError as erro:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(erro))