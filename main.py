import pyglet
from time import time as _time_now
def time_now():
    return int(_time_now() * 1000)
from os import getcwd
from random import randint
from math import sqrt
from pyglet.window import mouse
from pyglet.window import key

objects = {
    "enemy": [],
    "friendly_tower": [],
    "friendly_projectiles": [],
    "terrain": [],
    "player": [],
    "engine": [],
    "ui": []
}
batch = {
    "enemy": pyglet.graphics.Batch(),
    "friendly_tower": pyglet.graphics.Batch(),
    "friendly_tower_range": pyglet.graphics.Batch(),
    "terrain": pyglet.graphics.Batch(),
    "ui": pyglet.graphics.Batch(),
}

#window = pyglet.window.Window(width=1024, height=720)
window = pyglet.window.Window(width=1900, height=1060)
image_directory = (getcwd() + '\\assets\\graphic\\')
pyglet.resource.reindex()


class Enemy:
    z = 2

    def __init__(self, x, y, speed=20, max_hp=100, texture="error.png", path=(0, 0)):
        self.x = x
        self.y = y
        self.speed = speed
        self.max_hp = max_hp
        self.hp = self.max_hp
        self.tower_texture = pyglet.image.load(image_directory + texture)
        self.agro = pyglet.image.load(image_directory + "enemy_agro.png")
        self.hp_bar_texture = pyglet.image.load(image_directory + "health.png")
        self.enemy = pyglet.sprite.Sprite(img=self.tower_texture, x=x, y=y, batch=batch["enemy"])
        self.hp_bar = pyglet.sprite.Sprite(img=self.hp_bar_texture, x=x, y=y+32, batch=batch["enemy"])
        self.hp_bar.scale_x = 0
        self.path = path
        self.current_path = 0
        objects[self.type()].append(self)

    def move_to(self, pos):
        distance_x = (pos[0]-self.x)
        distance_y = (pos[1]-self.y)
        distance = sqrt(distance_x*distance_x+distance_y*distance_y)
        moves_remaining = distance / self.speed
        if moves_remaining < 1:
            self.x = pos[0]
            self.y = pos[1]
        else:
            self.x += distance_x/moves_remaining
            self.y += distance_y/moves_remaining

    def damage(self, dmg):
        self.enemy.image = self.agro
        self.hp -= dmg
        self.hp_bar.scale_x = self.hp / self.max_hp
        if self.is_alive():
            objects["player"][0].give_money(int(self.speed*1.3+self.max_hp*0.3))
            return "dead"
        return "alive"

    def is_alive(self):
        return self.hp <= 0

    def tick(self):
        if self.hp < self.max_hp:
            self.hp_bar.x = self.x-15
            self.hp_bar.y = self.y+17
        self.enemy.x = self.x - 15
        self.enemy.y = self.y - 15
        try:
            if (self.x, self.y) != self.path[self.current_path]:
                self.move_to(self.path[self.current_path])
            else:
                self.current_path += 1
        except IndexError:
            pass

    def draw(self):
        pass

    @staticmethod
    def type():
        return "enemy"


class Tower:
    z = 1

    def __init__(self, x, y, dmg=5, rang=150, rang_max=300, texture="error.png"):
        self.x = x
        self.y = y
        self.rang = rang
        self.rang_max = rang_max
        self.dmg = dmg
        tower_texture = pyglet.image.load(image_directory + texture)
        self.tower = pyglet.sprite.Sprite(img=tower_texture, batch=batch["friendly_tower"])
        tower_range_texture = pyglet.image.load(image_directory + "tower_range.png")
        self.tower_range = pyglet.sprite.Sprite(img=tower_range_texture, batch=batch["friendly_tower_range"])

        objects[self.type()].append(self)

    def tick(self):
        self.tower_range.scale = self.rang/50
        self.tower_range.x = self.x - self.rang
        self.tower_range.y = self.y - self.rang
        self.tower.x = self.x - 25
        self.tower.y = self.y - 40

        attacking = []
        for obj in objects["enemy"]:
            monster_x, monster_y = obj.x, obj.y
            if (monster_x-self.x)*(monster_x-self.x)+(monster_y-self.y)*(monster_y-self.y) <= self.rang*self.rang:
                attacking.append(obj)
        if len(attacking) > 0:
            if self.rang < self.rang_max:
                self.rang += 0.5
            closest = 1e4
            to_attack = None
            for enemy in attacking:
                distance = sqrt((enemy.x-self.x) * (enemy.x-self.x) + (enemy.y-self.y) * (enemy.y-self.y))
                if distance < closest:
                    closest = distance
                    to_attack = enemy
            if to_attack.damage(dmg=self.dmg) == "dead":
                objects["enemy"].remove(to_attack)

    def draw(self):
        pass

    @staticmethod
    def type():
        return "friendly_tower"


class Player:
    def __init__(self):
        self.selected_option = 0
        objects[self.type()].append(self)
        self.mouse_x = 0
        self.mouse_y = 0
        self.money = 1000
        self.money_label = pyglet.text.Label('Money: ?', font_name='Times New Roman', font_size=30, x=0,
                                             y=window.height - 90, batch=batch["ui"])

    def tick(self):
        self.money_label.text = "Money: " + str(self.money)

    def give_money(self, amount):
        self.money += amount

    def mouse_pressed(self, x, y, button, modifiers):
        if button == mouse.RIGHT and self.money > 500:
            self.money -= 500
            Tower(x, y, dmg=5, rang=200, texture="tower.png")

    def mouse_moved(self, x, y):
        self.mouse_x = x
        self.mouse_y = y

    def key_pressed(self, key_press, modifiers):
        if key_press == key.SPACE:
            objects["engine"][0].next_wave()
        if key_press == key._1 and self.money > 0:
            self.money -= 0
            Tower(self.mouse_x, self.mouse_y, dmg=5000, rang=100, rang_max=200, texture="tower.png")

    @staticmethod
    def type():
        return "player"


class Engine:
    def __init__(self):
        self.round_start = 0
        self.round_time = 30000
        self.round = -1
        self.path_1 = [
            (0, 108),
            (1690, 108),
            (1690, 920),
            (750, 920),
            (560, 790),
            (560, 0)
        ]
        self.waves = [
            # speed max_hp path
            [
                [3, 100, self.path_1],
                [3, 100, self.path_1],
                [3, 100, self.path_1],
                [3, 100, self.path_1],
                [3, 100, self.path_1]
            ],
            [
                [5, 150, self.path_1],
                [5, 150, self.path_1],
                [5, 150, self.path_1],
                [5, 150, self.path_1]
            ],
            [
                [1, 1000, self.path_1],
                [3, 150, self.path_1],
                [3, 150, self.path_1],
                [3, 150, self.path_1]
            ],
            [
                [3, 300, self.path_1],
                [2, 500, self.path_1],
                [3, 300, self.path_1],
                [3, 300, self.path_1],
                [2, 500, self.path_1],
                [3, 300, self.path_1],
            ],
            [
                [1, 5000, self.path_1],
                [5, 250, self.path_1],
                [5, 250, self.path_1],
                [5, 250, self.path_1],
                [5, 250, self.path_1],
                [5, 250, self.path_1],
                [5, 250, self.path_1],
                [5, 250, self.path_1],
                [5, 250, self.path_1],
                [5, 250, self.path_1],
                [5, 250, self.path_1]
            ],
            [
                [10, 250, self.path_1],
                [2, 750, self.path_1],
                [2, 750, self.path_1],
                [2, 750, self.path_1],
                [2, 750, self.path_1],
                [2, 750, self.path_1],
                [10, 250, self.path_1],
                [2, 750, self.path_1],
                [2, 750, self.path_1],
                [2, 750, self.path_1],
                [2, 750, self.path_1],
                [2, 750, self.path_1],
                [10, 250, self.path_1],
                [2, 750, self.path_1],
                [2, 750, self.path_1],
                [2, 750, self.path_1],
                [2, 750, self.path_1],
                [2, 750, self.path_1],
            ]
        ]
        self.to_spawn = []
        self.spawning = []
        self.spawn_timer = 1000
        self.last_spawned = 0
        objects[self.type()].append(self)

    def start_round(self):
        if self.round_start + self.round_time < time_now():
            if not (len(self.waves)-1 == self.round):
                self.round += 1
                if self.spawn_timer > 100:
                    self.spawn_timer -= 25
                self.to_spawn = self.waves[self.round]
                self.round_start = time_now()

    def next_wave(self):
        if (self.round_start + self.round_time - time_now()) / 1000 > 0:
            objects["player"][0].give_money(
                int(((self.round_start + self.round_time - time_now())/1000)*2.3)
            )
        for spawning in self.to_spawn:
            Enemy(self.path_1[0][0],
                  self.path_1[0][1],
                  speed=spawning[0],
                  max_hp=spawning[1],
                  path=spawning[2],
                  texture="enemy.png")
        self.to_spawn = []
        self.round_start = 0

    def tick(self):
        wave_timer.text = "Next round in " + str(int((self.round_start + self.round_time - time_now())/1000)) + "s"
        self.start_round()
        if self.last_spawned + self.spawn_timer < time_now() and self.to_spawn != []:
            self.spawning = self.to_spawn.pop(0)
            self.last_spawned = time_now()
            Enemy(self.path_1[0][0],
                  self.path_1[0][1],
                  speed=self.spawning[0],
                  max_hp=self.spawning[1],
                  path=self.spawning[2],
                  texture="enemy.png")

    @staticmethod
    def type():
        return "engine"


class Terrain:
    def __init__(self):
        terrain_image = pyglet.image.load(image_directory + "terrain.png")
        self.terrain = pyglet.sprite.Sprite(img=terrain_image, batch=batch["terrain"])
        objects[self.type()].append(self)

    def tick(self):
        pass

    @staticmethod
    def type():
        return "terrain"


def setup():
    global fps, wave_timer
    fps = pyglet.text.Label('FPS: ?', font_name='Times New Roman', font_size=30, x=0, y=window.height-30, batch=batch["ui"])
    wave_timer = pyglet.text.Label('Next wave in ?s', font_name='Times New Roman', font_size=30, x=0, y=window.height-60, batch=batch["ui"])

    Terrain()
    Engine()
    Player()


@window.event
def on_key_press(symbol, modifiers):
    objects["player"][0].key_pressed(symbol, modifiers)


@window.event
def on_mouse_press(x, y, button, modifiers):
    objects["player"][0].mouse_pressed(x, y, button, modifiers)



timers = {
    "update": 0,
    "draw": 0
}


def update(dt):
    fps.text = "FPS: " + str(int(pyglet.clock.get_fps()))
    if timers["update"] + (1000/60) < time_now():
        for typ, objs in objects.items():
            if typ == "terrain":
                continue
            for obj in objs:
                obj.tick()
        timers["update"] = time_now()


@window.event
def on_draw():
    window.clear()
    batch["terrain"].draw()
    batch["friendly_tower_range"].draw()
    batch["enemy"].draw()
    batch["friendly_tower"].draw()
    batch["ui"].draw()
    timers["draw"] = time_now()


@window.event
def on_mouse_motion(x, y, dx, dy):
    objects["player"][0].mouse_moved(x, y)


if __name__ == '__main__':
    # Loading
    setup()
    pyglet.clock.schedule(update)
    # Main run
    pyglet.app.run()
