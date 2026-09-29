from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_order_endpoint_authorized():
    response = client.get(
        "/api/orders/ORD-1005",
        params={"customer_id": "CUS-002"},
    )
    assert response.status_code == 200
    assert response.json()["order_id"] == "ORD-1005"


def test_order_endpoint_unauthorized():
    response = client.get(
        "/api/orders/ORD-1005",
        params={"customer_id": "CUS-001"},
    )
    assert response.status_code == 403
