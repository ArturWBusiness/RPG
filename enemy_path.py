import pyglet
from time import time as _time_now
def time_now():
    return int(_time_now() * 1000)
from os import getcwd
from random import randint
from math import sqrt
from pyglet.window import mouse

objects = []

window = pyglet.window.Window(width=1024, height=720)
#window = pyglet.window.Window(width=1900, height=1060)
image_directory = (getcwd() + '\\assets\\graphic\\')
pyglet.resource.reindex()


class Enemy:
    z = 1

    def __init__(self, x, y, max_hp=100, texture="error.png"):
        self.x = x
        self.y = y
        self.speed = 1
        self.max_hp = max_hp
        self.hp = self.max_hp
        self.tower_texture = pyglet.image.load(image_directory + texture)
        self.agro = pyglet.image.load(image_directory + "enemy_agro.png")
        self.hp_bar_texture = pyglet.image.load(image_directory + "health.png")
        self.sprite = pyglet.sprite.Sprite(img=self.tower_texture, x=x, y=y)
        self.hp_bar = pyglet.sprite.Sprite(img=self.hp_bar_texture, x=x, y=y)
        self.hp_bar.scale_x = 0
        self.path = [
            (100, 100),
            (100, 700),
            (600, 400),
            (100, 100),
            (10, 720)

        ]
        self.current_path = 0
        objects.append(self)

    def move_to(self, pos):
        distance_x = (pos[0]-self.x)
        distance_y = (pos[1]-self.y)
        distance = sqrt(distance_x*distance_x+distance_y*distance_y)
        moves_remaining = distance / self.speed
        if moves_remaining < self.speed:
            self.x = pos[0]
            self.y = pos[1]
        else:
            self.x += distance_x/moves_remaining
            self.y += distance_y / moves_remaining

    def tick(self):
        if (self.x, self.y) != self.path[self.current_path]:
            self.move_to(self.path[self.current_path])
        else:
            self.current_path += 1


    def draw(self):
        self.sprite.x = self.x-15
        self.sprite.y = self.y-15
        self.sprite.draw()


@window.event
def on_draw():
    window.clear()
    for obj in objects:
        obj.draw()
    fps.draw()


def setup():
    global fps
    fps = pyglet.text.Label('FPS:', font_name='Times New Roman', font_size=30, x=0, y=window.height-30)
    Enemy(100, 100, texture="enemy.png")


time_passed = 0
ii = 0
def update(dt):
    global time_passed, ii
    time_passed += dt
    ii += 1
    if time_passed >= 1:
        fps.text = "FPS: " + str(ii)
        ii = 0
        time_passed -= 1
    for obj in objects:
        obj.tick()


if __name__ == '__main__':
    # Loading
    setup()
    pyglet.clock.schedule(update)
    # Main run
    pyglet.app.run()
