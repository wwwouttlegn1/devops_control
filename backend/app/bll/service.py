from __future__ import annotations

from collections import OrderedDict
from decimal import Decimal, ROUND_HALF_UP
from typing import Sequence

from app.bll.errors import (
    InsufficientStockError,
    InvalidMedicineError,
    MedicineNotFoundError,
    NegativeStockError,
    OrderNotFoundError,
    PrescriptionRequiredError,
)
from app.dal.models import Medicine, Order, OrderItem
from app.dal.repository import PharmacyRepository

MONEY_STEP = Decimal("0.01")


class PharmacyService:
    def __init__(self, repository: PharmacyRepository) -> None:
        self._repository = repository

    def list_medicines(self, in_stock: bool | None = None) -> list[Medicine]:
        medicines = self._repository.list_medicines()
        if in_stock is True:
            return [medicine for medicine in medicines if medicine.quantity > 0]
        if in_stock is False:
            return [medicine for medicine in medicines if medicine.quantity == 0]
        return medicines

    def add_medicine(
        self,
        *,
        name: str,
        price: Decimal,
        quantity: int,
        prescription: bool,
    ) -> Medicine:
        normalized_name = name.strip()
        normalized_price = Decimal(str(price)).quantize(MONEY_STEP, rounding=ROUND_HALF_UP)
        if not normalized_name:
            raise InvalidMedicineError("Дәрі атауы бос болмауы керек")
        if normalized_price <= 0:
            raise InvalidMedicineError("Баға нөлден үлкен болуы керек")
        if quantity < 0:
            raise NegativeStockError("Қалдық теріс бола алмайды")
        return self._repository.add_medicine(
            name=normalized_name,
            price=normalized_price,
            quantity=quantity,
            prescription=prescription,
        )

    def update_stock(self, medicine_id: int, delta: int) -> Medicine:
        medicine = self._get_medicine(medicine_id)
        new_quantity = medicine.quantity + delta
        if new_quantity < 0:
            raise NegativeStockError("Қалдық теріс бола алмайды")
        updated = self._repository.set_stock(medicine_id, new_quantity)
        if updated is None:
            raise MedicineNotFoundError("Дәрі табылмады")
        return updated

    def create_order(
        self,
        *,
        requested_items: Sequence[tuple[int, int]],
        has_prescription: bool,
    ) -> Order:
        if not requested_items:
            raise InvalidMedicineError("Тапсырыс бос болмауы керек")

        aggregated: OrderedDict[int, int] = OrderedDict()
        for medicine_id, quantity in requested_items:
            if quantity <= 0:
                raise InvalidMedicineError("Дәрі саны нөлден үлкен болуы керек")
            aggregated[medicine_id] = aggregated.get(medicine_id, 0) + quantity

        selected: list[tuple[Medicine, int]] = []
        for medicine_id, quantity in aggregated.items():
            medicine = self._get_medicine(medicine_id)
            if medicine.prescription and not has_prescription:
                raise PrescriptionRequiredError(
                    f"{medicine.name} дәрісін сатып алу үшін рецепт қажет"
                )
            if medicine.quantity < quantity:
                raise InsufficientStockError(
                    f"{medicine.name} дәрісінің қоры жеткіліксіз"
                )
            selected.append((medicine, quantity))

        order_items: list[OrderItem] = []
        total = Decimal("0.00")
        for medicine, quantity in selected:
            subtotal = (medicine.price * quantity).quantize(
                MONEY_STEP, rounding=ROUND_HALF_UP
            )
            total += subtotal
            self._repository.set_stock(medicine.id, medicine.quantity - quantity)
            order_items.append(
                OrderItem(
                    medicine_id=medicine.id,
                    medicine_name=medicine.name,
                    quantity=quantity,
                    unit_price=medicine.price,
                    subtotal=subtotal,
                )
            )

        return self._repository.create_order(
            items=order_items,
            total=total.quantize(MONEY_STEP, rounding=ROUND_HALF_UP),
        )

    def get_order(self, order_id: int) -> Order:
        order = self._repository.get_order(order_id)
        if order is None:
            raise OrderNotFoundError("Тапсырыс табылмады")
        return order

    def _get_medicine(self, medicine_id: int) -> Medicine:
        medicine = self._repository.get_medicine(medicine_id)
        if medicine is None:
            raise MedicineNotFoundError("Дәрі табылмады")
        return medicine

