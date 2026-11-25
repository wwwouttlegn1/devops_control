from typing import Any

from fastapi import APIRouter, Query, status

from app.api.schemas import (
    HealthResponse,
    MedicineCreate,
    MedicineResponse,
    OrderCreate,
    OrderLineResponse,
    OrderResponse,
    StockUpdate,
)
from app.bll.service import PharmacyService


def create_api_router(service: PharmacyService) -> APIRouter:
    router = APIRouter()

    @router.get("/health", response_model=HealthResponse, tags=["system"])
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    @router.get(
        "/medicines", response_model=list[MedicineResponse], tags=["medicines"]
    )
    def list_medicines(
        in_stock: bool | None = Query(default=None),
    ) -> list[MedicineResponse]:
        return [
            MedicineResponse.model_validate(item)
            for item in service.list_medicines(in_stock=in_stock)
        ]

    @router.post(
        "/medicines",
        response_model=MedicineResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["medicines"],
    )
    def add_medicine(payload: MedicineCreate) -> MedicineResponse:
        medicine = service.add_medicine(**payload.model_dump())
        return MedicineResponse.model_validate(medicine)

    @router.patch(
        "/medicines/{medicine_id}/stock",
        response_model=MedicineResponse,
        tags=["medicines"],
    )
    def update_stock(medicine_id: int, payload: StockUpdate) -> MedicineResponse:
        medicine = service.update_stock(medicine_id, payload.delta)
        return MedicineResponse.model_validate(medicine)

    @router.post(
        "/orders",
        response_model=OrderResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["orders"],
    )
    def create_order(payload: OrderCreate) -> OrderResponse:
        order = service.create_order(
            requested_items=[(item.medicine_id, item.qty) for item in payload.items],
            has_prescription=payload.has_prescription,
        )
        return _order_response(order)

    @router.get(
        "/orders/{order_id}", response_model=OrderResponse, tags=["orders"]
    )
    def get_order(order_id: int) -> OrderResponse:
        return _order_response(service.get_order(order_id))

    return router


def _order_response(order: Any) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        total=order.total,
        items=[
            OrderLineResponse(
                medicine_id=item.medicine_id,
                medicine_name=item.medicine_name,
                qty=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
            )
            for item in order.items
        ],
    )

