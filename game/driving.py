from __future__ import annotations
import math
from ursina import Entity, color, held_keys, Vec3, destroy, camera, AmbientLight, DirectionalLight, window, application
from game.car import Car

class DrivingSession:
    def __init__(self, car: Car) -> None:
        self.car = car
        self.is_finished = False
        self.fuel = 100.0
        self.distance = 0.0
        self.wear = 0.0
        self.speed = 0.0
        self.angle = 0.0

        application.base.setBackgroundColor(10/255, 10/255, 15/255, 1)
        window.color = color.rgb(10, 10, 15)
        camera.clip_plane_near = 0.1
        camera.clip_plane_far = 200

        self.bg_quad = Entity(model='quad', scale=300, color=color.rgb(10, 10, 15), position=(0, 0, 80), rotation_x=180)
        self.ambient = AmbientLight(color=color.rgb(90, 90, 100))
        self.dir_light = DirectionalLight(position=(1, 2, -1), color=color.rgb(210, 210, 220))

        self.ground = Entity(model='plane', scale=200, color=color.rgb(25, 25, 30), collider='box', y=-0.5)
        self.car_entity = Entity(model='cube', color=color.rgb(52, 152, 219), scale=(1.5, 1, 3), y=0.5)

        camera.parent = None
        camera.position = Vec3(0, 6, -10)
        camera.rotation_x = -20
        camera.parent = self.car_entity

    def update(self) -> None:
        if self.fuel <= 0.0 or self.wear >= 100.0:
            self.is_finished = True
            self.car.condition -= int(self.wear * 0.3)
            self.car.needs_repair = self.car.condition < 100
            return

        if held_keys["up arrow"] or held_keys["w"]:
            self.speed += 0.2
        if held_keys["down arrow"] or held_keys["s"]:
            self.speed -= 0.15
        if held_keys["left arrow"] or held_keys["a"]:
            self.angle -= 2.0 if abs(self.speed) > 0.1 else 0
        if held_keys["right arrow"] or held_keys["d"]:
            self.angle += 2.0 if abs(self.speed) > 0.1 else 0

        self.speed *= 0.96
        self.speed = max(-2.0, min(4.0, self.speed))
        self.angle %= 360

        self.car_entity.rotation_y = self.angle
        rad = math.radians(self.angle)
        self.car_entity.x += math.sin(rad) * self.speed * 0.5
        self.car_entity.z += math.cos(rad) * self.speed * 0.5

        if abs(self.speed) > 0.05:
            self.distance += abs(self.speed) * 0.1
            self.fuel -= 0.05
            self.wear += 0.02

        if held_keys["escape"]:
            self.is_finished = True

    def render_ui(self, texts: list) -> None:
        texts[0].text = f"ТОПЛИВО: {self.fuel:.1f}%"
        texts[1].text = f"ИЗНОС: {self.wear:.1f}%"
        texts[2].text = f"ДИСТАНЦИЯ: {self.distance:.1f} км"
        texts[3].text = "ESC - ВЕРНУТЬСЯ"
        for i in range(4, len(texts)):
            texts[i].visible = False
        for i in range(4):
            texts[i].visible = True

    def cleanup(self) -> None:
        camera.parent = None
        camera.position = Vec3(0, 0, -10)
        camera.rotation = Vec3(0, 0, 0)
        
        destroy(self.car_entity)
        destroy(self.ground)
        destroy(self.bg_quad)
        destroy(self.ambient)
        destroy(self.dir_light)
        
        window.color = color.rgb(15, 15, 20)
        application.base.setBackgroundColor(15/255, 15/255, 20/255, 1)