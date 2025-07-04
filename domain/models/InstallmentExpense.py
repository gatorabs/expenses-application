from datetime import date
from dataclasses import dataclass, field

@dataclass
class InstallmentExpense:
    id: int
    name: str
    total: float
    n_parcels: int
    start_month: date
    current_parcel: int
    paid: bool
    affiliate: str