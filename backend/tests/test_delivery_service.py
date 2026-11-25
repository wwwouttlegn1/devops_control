from fastapi.testclient import TestClient

from delivery_service.main import app

client = TestClient(app)


def test_delivery_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_known_district_delivery_estimate() -> None:
    response = client.get("/delivery/estimate", params={"district": "Есіл"})

    assert response.status_code == 200
    assert response.json() == {"district": "Есіл", "days": 2}


def test_unknown_district_delivery_estimate() -> None:
    response = client.get("/delivery/estimate", params={"district": "Арал"})

    assert response.status_code == 200
    assert response.json()["days"] == 3

