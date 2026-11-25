from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MedicineCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    price: Annotated[Decimal, Field(gt=0, decimal_places=2)]
    quantity: Annotated[int, Field(ge=0)]
    prescription: bool = False


class MedicineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: Decimal
    quantity: int
    prescription: bool


class StockUpdate(BaseModel):
    delta: int

    @field_validator("delta")
    @classmethod
    def delta_must_not_be_zero(cls, value: int) -> int:
        if value == 0:
            raise ValueError("delta нөлге тең болмауы керек")
        return value


class OrderLineCreate(BaseModel):
    medicine_id: Annotated[int, Field(gt=0)]
    qty: Annotated[int, Field(gt=0)]


class OrderCreate(BaseModel):
    items: Annotated[list[OrderLineCreate], Field(min_length=1)]
    has_prescription: bool = False


class OrderLineResponse(BaseModel):
    medicine_id: int
    medicine_name: str
    qty: int
    unit_price: Decimal
    subtotal: Decimal


class OrderResponse(BaseModel):
    id: int
    items: list[OrderLineResponse]
    total: Decimal


class HealthResponse(BaseModel):
    status: str

