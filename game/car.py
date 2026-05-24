from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

@dataclass
class Part:
    name: str
    cost: int
    repair_value: int

PARTS_CATALOG: List[Part] = [
    Part("Двигатель", 15000, 40),
    Part("Шины", 8000, 25),
    Part("Аккумулятор", 6000, 20),
    Part("Тормоза", 10000, 30),
    Part("КПП", 20000, 35),
    Part("Подвеска", 12000, 25)
]

@dataclass
class Car:
    uid: int
    name: str
    base_price: int
    condition: int
    needs_repair: bool
    required_parts: List[str] = field(default_factory=list)
    owner_uid: str = "none"

    def calculate_market_value(self) -> int:
        base = int(self.base_price * 1.15)
        modifier = (self.condition - 50) / 100.0
        return max(base, int(base * (0.8 + modifier)))

    def apply_part(self, part: Part) -> bool:
        if part.name in self.required_parts:
            self.required_parts.remove(part.name)
            self.condition += part.repair_value
            if not self.required_parts:
                self.needs_repair = False
            return True
        return False

    def is_ready_to_drive(self) -> bool:
        return self.condition >= 100 and not self.needs_repair