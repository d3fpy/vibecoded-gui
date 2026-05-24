from ursina import Ursina, window, color, Entity, application
from game import Player, Car, Market, PartsShop, StateManager

app = Ursina()
window.title = "Car Flipper 3D"
window.borderless = False
window.fullscreen = False
window.fps_counter.enabled = False

application.base.setBackgroundColor(15/255, 15/255, 20/255, 1)
window.color = color.rgb(15, 15, 20)

bg = Entity(model='quad', scale=(100, 100), color=color.rgb(15, 15, 20), position=(0, 0, 50), rotation_x=180)

player = Player(starting_money=500200, starting_car=Car(uid=0, name="StartCar", base_price=35000, condition=100, needs_repair=False))
market = Market()
parts_shop = PartsShop()
state_mgr = StateManager(player, market, parts_shop)

def update():
    application.base.setBackgroundColor(15/255, 15/255, 20/255, 1)
    state_mgr.update()

def input(key: str):
    state_mgr.handle_input(key)

if __name__ == "__main__":
    app.run()