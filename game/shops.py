from __future__ import annotations
import random
from typing import List, Dict
from game.car import Car, Part, PARTS_CATALOG
from game.player import Player

class Market:
    def __init__(self) -> None:
        self.available_cars: List[Car] = []
        self._generate_initial_stock()

    def _generate_initial_stock(self) -> None:
        models = [
            ("Эконом Хэтчбек", 30000, ["Шины", "Аккумулятор"]),
            ("Классический Седан", 45000, ["Двигатель", "Тормоза"]),
            ("Грузовой Фургон", 70000, ["КПП", "Подвеска"]),
            ("Люкс Купе", 110000, ["Двигатель", "Шины", "Тормоза"])
        ]
        for idx, (name, price, needed) in enumerate(models):
            car = Car(
                uid=idx,
                name=name,
                base_price=price,
                condition=random.randint(30, 70),
                needs_repair=True,
                required_parts=needed.copy()
            )
            self.available_cars.append(car)

    def sell_car_to_player(self, player: Player, car_uid: int) -> bool:
        target_car = next((c for c in self.available_cars if c.uid == car_uid), None)
        if not target_car or not player.has_driven_once:
            return False
        price = target_car.calculate_market_value()
        if player.change_money(-price):
            player.add_car(target_car)
            self.available_cars.remove(target_car)
            return True
        return False

    def buy_car_from_player(self, player: Player, car_uid: int) -> bool:
        car = player.remove_car(car_uid)
        if not car:
            return False
        price = car.calculate_market_value()
        player.change_money(price)
        return True

class PartsShop:
    def __init__(self) -> None:
        self.stock: Dict[str, int] = {p.name: random.randint(2, 5) for p in PARTS_CATALOG}
        self.prices: Dict[str, int] = {p.name: p.cost for p in PARTS_CATALOG}

    def buy_part(self, player: Player, part_name: str) -> bool:
        if self.stock.get(part_name, 0) <= 0:
            return False
        cost = self.prices.get(part_name, 0)
        if not player.change_money(-cost):
            return False
        player.add_part(Part(part_name, cost, 0), 1)
        self.stock[part_name] -= 1
        return True

    def repair_car(self, player: Player, car_uid: int) -> bool:
        car = next((c for c in player.garage if c.uid == car_uid), None)
        if not car or not car.needs_repair:
            return False
        for needed_name in car.required_parts:
            if player.get_part_count(needed_name) > 0:
                part_data = next((p for p in PARTS_CATALOG if p.name == needed_name), None)
                if part_data:
                    player.remove_part(needed_name)
                    car.apply_part(part_data)
                    return True
        return False