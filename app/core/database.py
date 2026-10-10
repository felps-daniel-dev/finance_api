import os

from sqlmodel import SQLModel, Session, create_engine

from sqlalchemy.engine import URL

DATABASE_URL = URL.create(
    "postgresql+psycopg2",
    username="postgres",
    password="123456",
    host="localhost",
    port=5432,
    database="precificacao",
)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:123456@localhost:5432/precificacao",
)

# O engine é a "ponte" com o banco, criado uma vez só.
# pool_pre_ping=True testa a conexão antes de usá-la, evitando erro
# se o Postgres tiver fechado conexões antigas.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


# Cria no banco todas as tabelas dos modelos com table=True.
# Os modelos precisam ter sido importados antes, senão o SQLModel
# não sabe que eles existem.
def criar_tabelas() -> None:
    SQLModel.metadata.create_all(engine)


# Dependência do FastAPI: abre uma sessão para cada requisição e
# fecha sozinha no final (o "with" garante isso, mesmo se der erro).
# As rotas recebem a sessão com Depends(get_session).
def get_session():
    with Session(engine) as session:
        yield session