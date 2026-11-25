from fastapi import FastAPI, Query

app = FastAPI(title="Delivery service", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/delivery/estimate")
def estimate_delivery(
    district: str = Query(min_length=2, max_length=80),
) -> dict[str, str | int]:
    normalized = district.strip().lower()
    one_day = {"орталық", "центр", "center"}
    two_days = {
        "алматы",
        "байқоңыр",
        "есіл",
        "нұра",
        "сарайшық",
        "сарыарқа",
    }
    if normalized in one_day:
        days = 1
    elif normalized in two_days:
        days = 2
    else:
        days = 3
    return {"district": district.strip(), "days": days}

