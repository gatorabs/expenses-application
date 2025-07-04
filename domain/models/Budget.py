from datetime import date
from dataclasses import dataclass, field

@dataclass
class Budget:
    month: date
    limit: float