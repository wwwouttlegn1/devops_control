class DomainError(Exception):
    status_code = 400


class InvalidMedicineError(DomainError):
    status_code = 400


class MedicineNotFoundError(DomainError):
    status_code = 404


class OrderNotFoundError(DomainError):
    status_code = 404


class NegativeStockError(DomainError):
    status_code = 400


class PrescriptionRequiredError(DomainError):
    status_code = 403


class InsufficientStockError(DomainError):
    status_code = 409

