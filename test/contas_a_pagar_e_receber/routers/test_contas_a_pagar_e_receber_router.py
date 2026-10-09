from fastapi.testclient import TestClient

from main import app

##python -m pytest
client = TestClient(app)


def test_deve_listar_contas_a_pagar_e_receber():
    response = client.get("/contas-a-pagar-e-receber")

    assert response.status_code == 200

    assert response.json() == [
        {'id': 1, 'description': 'aluguel', 'valor': '705.0', 'tipo': 'PAGAR'},
        {'id': 1, 'description': 'cartão', 'valor': '870.98', 'tipo': 'PAGAR'}
    ]


def test_deve_criar_conta():
    nova_conta = {
        "description": "Mercado",
        "valor": 1000.00,
        "tipo": "PAGAR"
    }

    nova_conta_copy = nova_conta.copy()
    nova_conta_copy["id"] = 3
    nova_conta_copy["valor"] = "1000.0"

    response = client.post("/contas-a-pagar-e-receber/new", json=nova_conta)

    assert response.status_code == 201
    assert response.json() == nova_conta_copy