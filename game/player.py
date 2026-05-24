from __future__ import annotations
from typing import List, Dict, Optional
from game.car import Car, Part

class Player:
    def __init__(self, starting_money: int = 50000, starting_car: Optional[Car] = None) -> None:
        self.money: int = starting_money
        self.garage: List[Car] = []
        self.parts_inventory: Dict[str, int] = {}
        self.has_driven_once: bool = False
        if starting_car:
            self.garage.append(starting_car)

    def add_car(self, car: Car) -> None:
        car.owner_uid = "player"
        self.garage.append(car)

    def remove_car(self, car_uid: int) -> Optional[Car]:
        for idx, car in enumerate(self.garage):
            if car.uid == car_uid:
                return self.garage.pop(idx)
        return None

    def add_part(self, part: Part, quantity: int = 1) -> None:
        current_qty = self.parts_inventory.get(part.name, 0)
        self.parts_inventory[part.name] = current_qty + quantity

    def remove_part(self, part_name: str) -> bool:
        if self.parts_inventory.get(part_name, 0) > 0:
            self.parts_inventory[part_name] -= 1
            if self.parts_inventory[part_name] == 0:
                del self.parts_inventory[part_name]
            return True
        return False

    def get_part_count(self, part_name: str) -> int:
        return self.parts_inventory.get(part_name, 0)

    def change_money(self, amount: int) -> bool:
        if self.money + amount < 0:
            return False
        self.money += amount
        return True