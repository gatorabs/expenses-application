from dataclasses import dataclass, field

@dataclass
class FixedExpense:
    id: int
    name: str
    value: float
    due_day: int
    paid: bool
    affiliate: str  # banco, pessoa ou etc