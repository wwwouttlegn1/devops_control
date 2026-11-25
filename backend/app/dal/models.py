from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Medicine:
    id: int
    name: str
    price: Decimal
    quantity: int
    prescription: bool


@dataclass(frozen=True, slots=True)
class OrderItem:
    medicine_id: int
    medicine_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


@dataclass(frozen=True, slots=True)
class Order:
    id: int
    items: tuple[OrderItem, ...]
    total: Decimal

