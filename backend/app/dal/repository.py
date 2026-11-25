from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from threading import RLock
from typing import Protocol, Sequence

from app.dal.models import Medicine, Order, OrderItem


class PharmacyRepository(Protocol):
    def list_medicines(self) -> list[Medicine]: ...

    def get_medicine(self, medicine_id: int) -> Medicine | None: ...

    def add_medicine(
        self,
        *,
        name: str,
        price: Decimal,
        quantity: int,
        prescription: bool,
    ) -> Medicine: ...

    def set_stock(self, medicine_id: int, quantity: int) -> Medicine | None: ...

    def create_order(self, *, items: Sequence[OrderItem], total: Decimal) -> Order: ...

    def get_order(self, order_id: int) -> Order | None: ...


class InMemoryPharmacyRepository:
    """Thread-safe in-memory storage required by the assignment."""

    def __init__(self) -> None:
        self._medicines: dict[int, Medicine] = {}
        self._orders: dict[int, Order] = {}
        self._next_medicine_id = 1
        self._next_order_id = 1
        self._lock = RLock()

    def list_medicines(self) -> list[Medicine]:
        with self._lock:
            return list(self._medicines.values())

    def get_medicine(self, medicine_id: int) -> Medicine | None:
        with self._lock:
            return self._medicines.get(medicine_id)

    def add_medicine(
        self,
        *,
        name: str,
        price: Decimal,
        quantity: int,
        prescription: bool,
    ) -> Medicine:
        with self._lock:
            medicine = Medicine(
                id=self._next_medicine_id,
                name=name,
                price=price,
                quantity=quantity,
                prescription=prescription,
            )
            self._medicines[medicine.id] = medicine
            self._next_medicine_id += 1
            return medicine

    def set_stock(self, medicine_id: int, quantity: int) -> Medicine | None:
        with self._lock:
            medicine = self._medicines.get(medicine_id)
            if medicine is None:
                return None
            updated = replace(medicine, quantity=quantity)
            self._medicines[medicine_id] = updated
            return updated

    def create_order(self, *, items: Sequence[OrderItem], total: Decimal) -> Order:
        with self._lock:
            order = Order(
                id=self._next_order_id,
                items=tuple(items),
                total=total,
            )
            self._orders[order.id] = order
            self._next_order_id += 1
            return order

    def get_order(self, order_id: int) -> Order | None:
        with self._lock:
            return self._orders.get(order_id)

