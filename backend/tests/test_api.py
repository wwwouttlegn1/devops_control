from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.dal.repository import InMemoryPharmacyRepository
from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    repository = InMemoryPharmacyRepository()
    return TestClient(create_app(repository))


def create_medicine(
    client: TestClient,
    *,
    name: str = "Парацетамол",
    price: str = "350.00",
    quantity: int = 10,
    prescription: bool = False,
) -> dict:
    response = client.post(
        "/medicines",
        json={
            "name": name,
            "price": price,
            "quantity": quantity,
            "prescription": prescription,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_list_medicines(client: TestClient) -> None:
    created = create_medicine(client)

    response = client.get("/medicines")

    assert response.status_code == 200
    assert response.json()[0]["id"] == created["id"]


def test_in_stock_query_filter(client: TestClient) -> None:
    create_medicine(client, name="Бар", quantity=1)
    create_medicine(client, name="Жоқ", quantity=0)

    response = client.get("/medicines", params={"in_stock": "true"})

    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == ["Бар"]


def test_invalid_medicine_returns_422(client: TestClient) -> None:
    response = client.post(
        "/medicines",
        json={"name": "", "price": -1, "quantity": -2, "prescription": False},
    )

    assert response.status_code == 422


def test_patch_unknown_medicine_returns_404(client: TestClient) -> None:
    response = client.patch("/medicines/999/stock", json={"delta": 1})

    assert response.status_code == 404


def test_negative_stock_returns_400(client: TestClient) -> None:
    medicine = create_medicine(client, quantity=1)

    response = client.patch(
        f"/medicines/{medicine['id']}/stock", json={"delta": -2}
    )

    assert response.status_code == 400


def test_prescription_required_returns_403(client: TestClient) -> None:
    medicine = create_medicine(client, prescription=True)

    response = client.post(
        "/orders",
        json={
            "items": [{"medicine_id": medicine["id"], "qty": 1}],
            "has_prescription": False,
        },
    )

    assert response.status_code == 403


def test_insufficient_stock_returns_409(client: TestClient) -> None:
    medicine = create_medicine(client, quantity=1)

    response = client.post(
        "/orders",
        json={
            "items": [{"medicine_id": medicine["id"], "qty": 2}],
            "has_prescription": True,
        },
    )

    assert response.status_code == 409


def test_create_and_get_order_with_total(client: TestClient) -> None:
    medicine = create_medicine(client, price="125.50", quantity=4)
    create_response = client.post(
        "/orders",
        json={
            "items": [{"medicine_id": medicine["id"], "qty": 2}],
            "has_prescription": False,
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert Decimal(created["total"]) == Decimal("251.00")

    get_response = client.get(f"/orders/{created['id']}")
    assert get_response.status_code == 200
    assert get_response.json() == created


def test_empty_order_returns_422(client: TestClient) -> None:
    response = client.post(
        "/orders", json={"items": [], "has_prescription": False}
    )

    assert response.status_code == 422

