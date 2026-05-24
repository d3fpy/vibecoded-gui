from __future__ import annotations
import math
from ursina import Text, color, camera
from enum import Enum
from typing import List, Optional
from game.player import Player
from game.shops import Market, PartsShop
from game.driving import DrivingSession
from game.car import Car

class GameState(Enum):
    HOME = "home"
    MARKET = "market"
    PARTS_SHOP = "parts_shop"
    GARAGE = "garage"
    DRIVING = "driving"

class StateManager:
    def __init__(self, player: Player, market: Market, parts_shop: PartsShop) -> None:
        self.player = player
        self.market = market
        self.parts_shop = parts_shop
        self.current_state = GameState.HOME
        self.selected_index = 0
        self.messages: List[str] = ["Система готова."]
        self.driving_session: Optional[DrivingSession] = None
        self.ui_texts: List[Text] = []
        self.garage_view: str = "list"
        self.garage_car_idx: int = 0
        self.anim_progress: float = 1.0
        self.rgb_phase: float = 0.0
        self._build_ui()

    def _build_ui(self) -> None:
        for i in range(16):
            txt = Text(
                text="",
                scale=0.85,
                y=0.45 - i * 0.065,
                x=0,
                origin=(0.5, 0.5),
                color=color.white,
                visible=False
            )
            self.ui_texts.append(txt)

    def _trigger_animation(self) -> None:
        self.anim_progress = 0.0

    def update(self) -> None:
        self.rgb_phase += 0.04
        if self.anim_progress < 1.0:
            self.anim_progress += 0.14

        if self.current_state == GameState.DRIVING and self.driving_session:
            self.driving_session.update()
            if self.driving_session.is_finished:
                self.player.has_driven_once = True
                self.driving_session.cleanup()
                self.current_state = GameState.GARAGE
                self.garage_view = "list"
                self.add_message("Первый заезд завершён. Рынок открыт.")
                self.selected_index = 0
                self._trigger_animation()
            self.driving_session.render_ui(self.ui_texts)
            return

        self._update_menu_text()

    def handle_input(self, key: str) -> None:
        if self.current_state == GameState.DRIVING:
            return
        if key in ("up arrow", "w"):
            self.selected_index = max(0, self.selected_index - 1)
        elif key in ("down arrow", "s"):
            self.selected_index = min(self._get_max_index() - 1, self.selected_index + 1)
        elif key in ("enter", "return"):
            self._execute_selected()
        elif key == "escape":
            if self.current_state != GameState.HOME:
                if self.current_state == GameState.GARAGE and self.garage_view == "detail":
                    self.garage_view = "list"
                    self.selected_index = 0
                    self._trigger_animation()
                    return
                self.current_state = GameState.HOME
                self.garage_view = "list"
                self.selected_index = 0
                self._trigger_animation()

    def _get_max_index(self) -> int:
        if self.current_state == GameState.HOME:
            return 3
        if self.current_state == GameState.MARKET:
            return len(self.market.available_cars) + (1 if self.player.garage else 0)
        if self.current_state == GameState.PARTS_SHOP:
            return len(self.parts_shop.stock)
        if self.current_state == GameState.GARAGE:
            if self.garage_view == "list":
                return len(self.player.garage)
            return 3
        return 0

    def _execute_selected(self) -> None:
        if self.current_state == GameState.HOME:
            transitions = [GameState.MARKET, GameState.PARTS_SHOP, GameState.GARAGE]
            target = transitions[self.selected_index]
            if target == GameState.MARKET and not self.player.has_driven_once:
                self.add_message("Сначала совершите первую поездку.")
                return
            self.current_state = target
            self.selected_index = 0
            self._trigger_animation()
            return

        if self.current_state == GameState.MARKET:
            if self.selected_index < len(self.market.available_cars):
                car = self.market.available_cars[self.selected_index]
                success = self.market.sell_car_to_player(self.player, car.uid)
                self.add_message("Покупка успешна." if success else "Недостаточно средств.")
            elif self.player.garage:
                success = self.market.buy_car_from_player(self.player, self.player.garage[0].uid)
                self.add_message("Продажа успешна." if success else "Ошибка продажи.")
            return

        if self.current_state == GameState.PARTS_SHOP:
            part_names = list(self.parts_shop.stock.keys())
            if self.selected_index < len(part_names):
                name = part_names[self.selected_index]
                success = self.parts_shop.buy_part(self.player, name)
                self.add_message(f"Куплено: {name}." if success else "Нет в наличии.")
            return

        if self.current_state == GameState.GARAGE:
            if self.garage_view == "list":
                if self.selected_index < len(self.player.garage):
                    self.garage_car_idx = self.selected_index
                    self.garage_view = "detail"
                    self.selected_index = 0
                    self._trigger_animation()
            else:
                car = self.player.garage[self.garage_car_idx]
                if self.selected_index == 0:
                    success = self.parts_shop.repair_car(self.player, car.uid)
                    self.add_message("Деталь установлена." if success else "Нет нужных запчастей.")
                    self._trigger_animation()
                elif self.selected_index == 1:
                    if car.is_ready_to_drive():
                        self.driving_session = DrivingSession(car)
                        self.current_state = GameState.DRIVING
                        self.add_message("Двигатель запущен.")
                    else:
                        self.add_message("Требуется ремонт.")
                elif self.selected_index == 2:
                    self.garage_view = "list"
                    self.selected_index = 0
                    self._trigger_animation()
            return

    def add_message(self, text: str) -> None:
        self.messages.append(text)
        if len(self.messages) > 3:
            self.messages.pop(0)

    def _update_menu_text(self) -> None:
        alpha = int(255 * min(1.0, self.anim_progress * 1.8))
        y_shift = (1.0 - self.anim_progress) * 0.04
        base_y = 0.45

        r = int(128 + 127 * math.sin(self.rgb_phase))
        g = int(128 + 127 * math.sin(self.rgb_phase + 2.094))
        b = int(128 + 127 * math.sin(self.rgb_phase + 4.188))

        lines = [f"БАЛАНС: ${self.player.money}", f"РАЗДЕЛ: {self.current_state.value.upper()}", ""]
        max_idx = self._get_max_index()

        for i in range(max_idx):
            prefix = "> " if i == self.selected_index else "  "
            label = self._get_label(i)
            lines.append(f"{prefix}{label}")

        lines.append("")
        lines.extend(self.messages[-3:])

        for i in range(len(self.ui_texts)):
            if i < len(lines):
                self.ui_texts[i].text = lines[i]
                self.ui_texts[i].visible = True
                self.ui_texts[i].y = base_y - i * 0.065 - y_shift
                if i == 0:
                    self.ui_texts[i].color = color.rgba(46, 204, 113, alpha)
                elif i == 1:
                    self.ui_texts[i].color = color.rgba(r, g, b, alpha)
                elif i == self.selected_index + 2:
                    self.ui_texts[i].color = color.rgba(255, 255, 255, alpha)
                else:
                    self.ui_texts[i].color = color.rgba(189, 195, 199, alpha)
            else:
                self.ui_texts[i].visible = False

    def _get_label(self, index: int) -> str:
        if self.current_state == GameState.HOME:
            return ["РЫНОК АВТО", "МАГАЗИН ЗАПЧАСТЕЙ", "ГАРАЖ"][index]
        if self.current_state == GameState.MARKET:
            if index < len(self.market.available_cars):
                c = self.market.available_cars[index]
                missing = ", ".join(c.required_parts) if c.required_parts else "Исправна"
                return f"{c.name} | СОСТОЯНИЕ: {c.condition}% | ЦЕНА: ${c.calculate_market_value()} | НУЖНЫ: {missing}"
            return "ПРОДАТЬ МАШИНУ"
        if self.current_state == GameState.PARTS_SHOP:
            names = list(self.parts_shop.stock.keys())
            if index < len(names):
                return f"{names[index]} | В НАЛИЧИИ: {self.parts_shop.stock[names[index]]} | ЦЕНА: ${self.parts_shop.prices[names[index]]}"
            return "ПУСТО"
        if self.current_state == GameState.GARAGE:
            if self.garage_view == "list":
                if index < len(self.player.garage):
                    c = self.player.garage[index]
                    status = "ИСПРАВНА" if c.is_ready_to_drive() else "ТРЕБУЕТ РЕМОНТА"
                    return f"{c.name} | {status}"
                return "ПУСТО"
            else:
                car = self.player.garage[self.garage_car_idx]
                missing = ", ".join(car.required_parts) if car.required_parts else "Нет"
                if index == 0:
                    return f"УСТАНОВИТЬ ДЕТАЛЬ | ТРЕБУЮТСЯ: {missing}"
                elif index == 1:
                    status = "ГОТОВО К ЕЗДЕ" if car.is_ready_to_drive() else "НЕЛЬЗЯ ЕХАТЬ"
                    return f"ПОЕХАТЬ | {status} | ИЗНОС: {car.condition}%"
                elif index == 2:
                    return "НАЗАД К СПИСКУ"
        return "НЕИЗВЕСТНО"
