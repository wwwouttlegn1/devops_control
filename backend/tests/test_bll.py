from decimal import Decimal

import pytest

from app.bll.errors import (
    InsufficientStockError,
    InvalidMedicineError,
    MedicineNotFoundError,
    NegativeStockError,
    OrderNotFoundError,
    PrescriptionRequiredError,
)
from app.bll.service import PharmacyService
from app.dal.repository import InMemoryPharmacyRepository


@pytest.fixture
def service() -> PharmacyService:
    # A fresh repository is injected for every test: no global API storage is used.
    return PharmacyService(InMemoryPharmacyRepository())


def add_medicine(
    service: PharmacyService,
    *,
    name: str = "Парацетамол",
    price: str = "100.00",
    quantity: int = 10,
    prescription: bool = False,
):
    return service.add_medicine(
        name=name,
        price=Decimal(price),
        quantity=quantity,
        prescription=prescription,
    )


def test_add_medicine_normalizes_name_and_price(service: PharmacyService) -> None:
    medicine = add_medicine(service, name="  Ибупрофен  ", price="120.555")

    assert medicine.name == "Ибупрофен"
    assert medicine.price == Decimal("120.56")


def test_list_medicines_filters_stock(service: PharmacyService) -> None:
    add_medicine(service, name="Бар", quantity=2)
    add_medicine(service, name="Жоқ", quantity=0)

    assert [item.name for item in service.list_medicines(in_stock=True)] == ["Бар"]
    assert [item.name for item in service.list_medicines(in_stock=False)] == ["Жоқ"]


def test_add_medicine_rejects_blank_name(service: PharmacyService) -> None:
    with pytest.raises(InvalidMedicineError):
        add_medicine(service, name="   ")


def test_add_medicine_rejects_negative_stock(service: PharmacyService) -> None:
    with pytest.raises(NegativeStockError):
        add_medicine(service, quantity=-1)


def test_update_stock_changes_quantity(service: PharmacyService) -> None:
    medicine = add_medicine(service, quantity=5)

    updated = service.update_stock(medicine.id, -2)

    assert updated.quantity == 3


def test_update_stock_cannot_be_negative(service: PharmacyService) -> None:
    medicine = add_medicine(service, quantity=1)

    with pytest.raises(NegativeStockError):
        service.update_stock(medicine.id, -2)


def test_prescription_medicine_is_forbidden_without_prescription(
    service: PharmacyService,
) -> None:
    medicine = add_medicine(service, prescription=True)

    with pytest.raises(PrescriptionRequiredError):
        service.create_order(
            requested_items=[(medicine.id, 1)], has_prescription=False
        )


def test_insufficient_stock_raises_conflict(service: PharmacyService) -> None:
    medicine = add_medicine(service, quantity=1)

    with pytest.raises(InsufficientStockError):
        service.create_order(
            requested_items=[(medicine.id, 2)], has_prescription=True
        )


def test_order_calculates_total_and_decreases_stock(service: PharmacyService) -> None:
    first = add_medicine(service, price="125.50", quantity=5)
    second = add_medicine(service, name="Дәрумен", price="200", quantity=4)

    order = service.create_order(
        requested_items=[(first.id, 2), (second.id, 1)],
        has_prescription=True,
    )

    assert order.total == Decimal("451.00")
    assert service.list_medicines()[0].quantity == 3
    assert service.list_medicines()[1].quantity == 3


def test_duplicate_order_lines_are_aggregated(service: PharmacyService) -> None:
    medicine = add_medicine(service, price="50", quantity=6)

    order = service.create_order(
        requested_items=[(medicine.id, 2), (medicine.id, 3)],
        has_prescription=False,
    )

    assert len(order.items) == 1
    assert order.items[0].quantity == 5
    assert order.total == Decimal("250.00")
    assert service.list_medicines()[0].quantity == 1


def test_unknown_medicine_and_order_raise_not_found(service: PharmacyService) -> None:
    with pytest.raises(MedicineNotFoundError):
        service.update_stock(999, 1)
    with pytest.raises(OrderNotFoundError):
        service.get_order(999)

