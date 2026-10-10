from contextlib import asynccontextmanager

from fastapi import FastAPI

# Importar o modelo (mesmo sem usar direto) registra a tabela no
# SQLModel. Sem isso, criar_tabelas() não criaria a tabela "conta".
from app.models import conta  # noqa: F401
from app.core.database import criar_tabelas
from app.routers import conta_routers


# "lifespan" é o jeito atual de rodar código quando a aplicação
# sobe (antes do yield) e quando desliga (depois do yield).
# Substitui o antigo @app.on_event("startup").
@asynccontextmanager
async def lifespan(app: FastAPI):
    criar_tabelas()
    yield


app = FastAPI(title="API de Exemplo - Contas", lifespan=lifespan)

# Registra as rotas de contas no app principal.
app.include_router(conta_routers.router)


# Só executa quando o arquivo é rodado diretamente (botão Run).
# Sobe o servidor Uvicorn, que fica rodando até você parar.
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", reload=True)