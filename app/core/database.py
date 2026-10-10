from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = "postgres:///postgres@localhost"

# O engine é a "ponte" com o banco, criado uma vez só.
# check_same_thread=False é necessário no SQLite com FastAPI, porque
# o FastAPI pode usar threads diferentes na mesma requisição.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


# Cria no banco todas as tabelas dos modelos com table=True.
# Os modelos precisam ter sido importados antes
# senão o SQLModel não sabe que eles existem.
def criar_tabelas() -> None:
    SQLModel.metadata.create_all(engine)


# Dependência do FastAPI: abre uma sessão para cada requisição e
# fecha sozinha no final (o "with" garante isso, mesmo se der erro).
# As rotas recebem a sessão com Depends(get_session).
def get_session():
    with Session(engine) as session:
        yield session