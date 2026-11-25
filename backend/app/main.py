from __future__ import annotations

import os
from decimal import Decimal

from fastapi import FastAPI

from app.api.errors import register_error_handlers
from app.api.routes import create_api_router
from app.bll.service import PharmacyService
from app.dal.repository import InMemoryPharmacyRepository, PharmacyRepository


def create_app(
    repository: PharmacyRepository | None = None,
    *,
    seed_demo: bool = False,
) -> FastAPI:
    storage = repository or InMemoryPharmacyRepository()
    service = PharmacyService(storage)

    if seed_demo:
        _seed_demo_data(service)

    application = FastAPI(
        title="Дәріхана API",
        version="1.0.0",
        description="5-нұсқа: дәрілер мен тапсырыстарды басқару API-і",
    )
    register_error_handlers(application)
    application.include_router(create_api_router(service))
    application.state.repository = storage
    return application


def _seed_demo_data(service: PharmacyService) -> None:
    service.add_medicine(
        name="Парацетамол",
        price=Decimal("350.00"),
        quantity=24,
        prescription=False,
    )
    service.add_medicine(
        name="Амоксициллин",
        price=Decimal("1450.00"),
        quantity=8,
        prescription=True,
    )
    service.add_medicine(
        name="Дәрумен C",
        price=Decimal("890.00"),
        quantity=0,
        prescription=False,
    )


app = create_app(
    seed_demo=os.getenv("PHARMACY_SEED_DEMO", "false").lower() in {"1", "true", "yes"}
)

