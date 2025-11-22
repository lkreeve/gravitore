# title: Gravitore
# author: Lance Reeve

import pyxel
import math
import random
from collections import Counter

SCREEN_WIDTH = 256
SCREEN_HEIGHT = 256

SOLID = [
    (1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),(8,0),(9,0),(10,0),(11,0),

    (6,6),(7,6),(8,6),(9,6),(12,6),(13,6),(14,6), (0,10),(0,11),(1,10),(1,11),(2,10), (8,9),(9,9),(8,10),(9,10),
    
    (0, 3), (0, 4), (0, 5),
    (1, 3), (1, 4), (1, 5),
    (2, 3), (2, 4), (2, 5),
    
    (3, 3), (3, 4), (3, 5),
    (4, 3), (4, 4), (4, 5),
    (5, 3), (5, 4), (5, 5),

    (6, 3), (6, 4), (6, 5),
    (7, 3), (7, 4), (7, 5),
    (8, 3), (8, 4), (8, 5),

    (9, 3), (9, 4), (9, 5),
    (10, 3), (10, 4), (10, 5),
    (11, 3), (11, 4), (11, 5),

    (12, 3), (12, 4), (12, 5),
    (13, 3), (13, 4), (13, 5),
    (14, 3), (14, 4), (14, 5)

]
# same index as solid, just has the initial mining times
MINE_T = [
    0.25, 999999999999, 1, 2.5, 3, 5, 6, 12, 12, 20, 20,

    4, 4, 4, 0.25, 18, 18, 18, 1,1,1,1,1, 4,4,4,4,

    0.5, 0.5, 0.5,
    0.5, 0.5, 0.5,
    0.5, 0.5, 0.5,

    2, 2, 2,
    2, 2, 2,
    2, 2, 2,

    4, 4, 4,
    4, 4, 4,
    4, 4, 4,

    8, 8, 8,
    8, 8, 8,
    8, 8, 8,

    16, 16, 16,
    16, 16, 16,
    16, 16, 16
    
]

PRICES = [
    2, 1, 5, 250, 300, 500, 600, 1200, 1200, 5000, 5000,

    40, 40, 40, 2, 180, 180, 180, 1000000,1000000,1000000,1000000,1000000, 40,40,40,40,

    5, 5, 5,
    5, 5, 5,
    5, 5, 5,

    20, 20, 20,
    20, 20, 20,
    20, 20, 20,

    40, 40, 40,
    40, 40, 40,
    40, 40, 40,

    80, 80, 80,
    80, 80, 80,
    80, 80, 80,

    160, 160, 160,
    160, 160, 160,
    160, 160, 160
]

HYPER_DRIVE = [(0,12), (1, 12), (0, 13), (1, 13)]

SHOPPING_TILES = [(0,7), (1,7), (2,7), (3,7), (0, 12), (1, 12), (0, 13), (1, 13)]

# x, y, gravity radius in tiles
planets = []

def append_objects():
    ################### in tiles
    planets.append(Planet(48, 48, 12))
    planets.append(Planet(208, 48, 16))
    planets.append(Planet(128, 128, 32))
    planets.append(Planet(56, 200, 24))
    planets.append(Planet(200, 200, 24))
    planets.append(Planet(36, 116, 4))

# abreviation
def get_tile(tile_x, tile_y, tilemap):
    return pyxel.tilemaps[tilemap].pget(tile_x, tile_y)

def set_tile(tile_x, tile_y, tile, tilemap):
    return pyxel.tilemaps[tilemap].pset(tile_x, tile_y, tile)

# if two abjects are colliding
def is_colliding(x1, x2, y1, y2, w1, w2, h1, h2):
        if x1 + w1 >= x2 and x1 <= x2 + w2 and y1 + h1 >= y2 and y1 <= y2 + h2:
            return True

# find location of tiles
def find_tile(level_x, level_y, tile_list):
    list_of_tiles = []
    for x in range(pyxel.floor(level_x * (SCREEN_WIDTH / 8)), pyxel.floor(level_x * (SCREEN_WIDTH / 8) + (SCREEN_WIDTH / 8))):
        for y in range(pyxel.floor(level_y * (SCREEN_HEIGHT / 8)), pyxel.floor(level_y * (SCREEN_HEIGHT / 8) + (SCREEN_HEIGHT / 8))):
            if get_tile(x, y) in tile_list:
                list_of_tiles.append((x * 8, y * 8))
    return(list_of_tiles)

# if object colliding with a list of tiles
def is_colliding_with_tile(x, y, w, h, tile_list, tilemap):
    is_colliding = False
    
    x = pyxel.floor(x)
    y = pyxel.floor(y)
    for yi in range(y, y + h - 1):
        for xi in range(x, x + w - 1):
            if get_tile(xi // 8, yi // 8, tilemap) in tile_list:
                is_colliding = True
    
    return is_colliding

# this makes all the dead things in a list go away
def cleanup_list(list):
    i = 0
    while i < len(list):
        elem = list[i]
        if elem.is_alive:
            i += 1
        else:
            list.pop(i)

# this converts color to str and if its bigger than 9 than it turns into a letter
# order of colors goes: 123456789abcdef
def convert_color(color):
    if color > 9:
        if color == 10:
            c = "a"
        if color == 11:
            c = "b"
        if color == 12:
            c = "c"
        if color == 13:
            c = "d"
        if color == 14:
            c = "e"
        if color == 15:
            c = "f"
    else: 
        c = str(color)
    
    return c

def draw_circle_mask():
    pyxel.blt(0 + camera.x, 0 + camera.y, 2, 0, 0, 128, 128, 14)
    pyxel.blt(0 + camera.x, 128 + camera.y, 2, 0, 0, 128, 128, 14, 270)
    pyxel.blt(128 + camera.x, 128 + camera.y, 2, 0, 0, 128, 128, 14, 180)
    pyxel.blt(128 + camera.x, 0 + camera.y, 2, 0, 0, 128, 128, 14, 90)

def get_color_and_dither(player_x, player_y, planet_x, planet_y):
    # Distance thresholds
    d1 = 128     # Full light blue
    d2 = 192    # Fading to dark blue
    d3 = 256    # Fading to black

    # Pyxel color indices
    LIGHT_BLUE = 12
    DARK_BLUE = 1
    BLACK = 0

    # Distance calculation
    dx = player_x - planet_x
    dy = player_y - planet_y
    dist = (dx * dx + dy * dy) ** 0.5

    if dist <= d1:
        color = LIGHT_BLUE
        dither_level = 0.0  # solid
    elif dist <= d2:
        t = (dist - d1) / (d2 - d1)
        color = DARK_BLUE
        dither_level = 0.5 * t
    elif dist <= d3:
        t = (dist - d2) / (d3 - d2)
        color = BLACK
        dither_level = 0.5 + 0.5 * t
    else:
        color = BLACK
        dither_level = 1.0  # completely invisible

    return color, dither_level

def draw_text_with_outline(x, y, text, text_color, outline_color):
    offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # left, right, up, down
    for dx, dy in offsets:
        pyxel.text(x + dx, y + dy, text, outline_color)
    pyxel.text(x, y, text, text_color)

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.xv = 0
        self.yv = 0
        self.ro = 0
        self.sc = 1
        self.center_x = 128
        self.center_y = 128
        self.rotation_speed = 10  # Adjust this for how fast the camera rotates (degrees per frame)
        self.target_ro = 0  # Target rotation angle in degrees
        self.transition_time = 0  # The time that has passed since we started rotating
        self.max_transition_time = 15
        self.zoom = 1

    def update(self):
        ######## update rotation ##############
        if player.gravitational:
            if player.gdirection == 0:
                self.target_ro = 0
            if player.gdirection == 1:
                self.target_ro = 90
            if player.gdirection == 2:
                self.target_ro = 180
            if player.gdirection == 3:
                self.target_ro = 270
        else: 
            self.target_ro = player.ro
            
        # Calculate the difference between current and target rotation
        delta_ro = self.target_ro - self.ro
        
        # Normalize the delta to keep the rotation smooth and avoid overshooting
        if delta_ro > 180:
            delta_ro -= 360
        elif delta_ro < -180:
            delta_ro += 360

        # Interpolate the rotation smoothly using the sine function
        # We use math.sin() to create a smooth easing effect
        step = math.sin(delta_ro * math.pi / 180) * self.rotation_speed

        # Update the current rotation towards the target rotation
        self.ro += step
        
        # Ensure the rotation stays within the 0-360 degree range
        self.ro = self.ro % 360

        ########## update x and y ###############

        self.x = player.x - SCREEN_WIDTH / 2
        self.y = player.y - SCREEN_HEIGHT / 2

class Particle:
    def __init__(self, x, y, vx, vy, ax, ay, size, color, lifespan, shape="circle", gravity=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.ax = ax
        self.ay = ay + gravity
        self.size = size
        self.initial_size = size
        self.color = color
        self.lifespan = lifespan
        self.initial_lifespan = lifespan
        self.shape = shape

    def update(self):
        self.vx += self.ax
        self.vy += self.ay
        self.x += self.vx
        self.y += self.vy
        self.lifespan -= 1
        life_ratio = self.lifespan / self.initial_lifespan
        # self.size = 0.2 + self.size * life_ratio
        self.size = self.initial_size * (self.lifespan / self.initial_lifespan)

    def draw(self):
        if self.shape == "circle":
            pyxel.circ(self.x, self.y, self.size, self.color)
        elif self.shape == "square":
            pyxel.rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2, self.color)


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, count=5, **kwargs):
        for _ in range(count):
            vx = kwargs.get('vx', random.uniform(-1, 1))
            vy = kwargs.get('vy', random.uniform(-1, 1))
            ax = kwargs.get('ax', 0)
            ay = kwargs.get('ay', 0)
            size = kwargs.get('size', random.uniform(1, 3))
            color = kwargs.get('color', random.randint(1, 15))
            lifespan = kwargs.get('lifespan', random.randint(30, 60))
            shape = kwargs.get('shape', 'circle')
            gravity = kwargs.get('gravity', 0)

            particle = Particle(x, y, vx, vy, ax, ay, size, color, lifespan, shape, gravity)
            self.particles.append(particle)

    def update(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.lifespan <= 0:
                self.particles.remove(particle)

    def draw(self):
        for particle in self.particles:
            particle.draw()
class Player:
    def __init__(self):
        self.x = 120 + 256
        self.y = 64 + 256
        self.xv = 0
        self.yv = 0
        self.speed = 1.2
        self.friction = 0.7
        self.g = 0.5
        # jetpack power
        self.j = 1
        
        #V 0 up, 1 right, 2 down, 3 left V#
        self.gdirection = 0
        self.grounded = False
        self.ceilfast = False
        self.w = 8
        self.h = 8
        # rotation
        self.ro = 0
        # only what user sees
        self.dro = 0
        # rotational velocity
        self.rov = 0
        # forward (just a vector of (x, y))
        self.f = 0
        # speed of ship
        self.fspeed = 0.4
        # forward velocity
        self.fv = 0
        # scale
        self.sc = 1
        # the atmosphere the player is in
        self.planet_x = 0
        self.planet_y = 0
        # counts the amount of planets that the player is in the gravitational field of (will always be 1 or 0)
        self.planet_counter = 0
        # if player is near enough to a planet to experience gravity
        self.gravitational = False
        # nearest planet
        self.nearest_planet_index = 0

        # 0 is not mining, 1 up, 2 right, 3 down, 4 left
        self.mining_d = 0
        self.mining_x = 0
        self.mining_y = 0
        # mining time
        self.mining_t = -1
        # old tile selected
        self.old_mining_x = 0
        self.old_mining_y = 0
        self.mining = False

        # Mine speed, amount mined each frame, higher the faster speed
        self.mining_speed = 1

        self.frame = 0
        self.max_frame = 3
        self.direction_x = 1
        self.direction_y = 1
        self.max_frame_count = 1
        self.frame_count = 0
        self.just_grounded = False
        self.visible = True

        # list of all the indexes of the tiles youve mined before selling them
        self.backpack = []
        # money
        self.money = 0
        self.show_downkey = True
        # storage capacity
        self.capacity = 10
        # fuel capactiy
        self.fuel_cap = 800
        self.fuel = self.fuel_cap
        self.price_of_pick = 60
        self.price_of_cap = 60
        self.price_of_fuel = 60

        self.game_fin = False

        # death
        self.dead = False

    def get_gravity(self, x, y, origin_x, origin_y):
        if self.planet_x == 0 and self.planet_y == 0:
            return 0
        else:
            # Shift the coordinates relative to the origin
            x_rel = x - origin_x
            y_rel = y - origin_y
                
            # Shift the coordinates relative to the origin
            x_rel = x - origin_x
            y_rel = y - origin_y

            # Adjust the conditions to make "Above" or "Below" diagonals inclusive by 2 pixels
            if y_rel >= x_rel and y_rel >= -x_rel:
                return 2
            elif y_rel <= x_rel and y_rel <= -x_rel:
                return 0

            # Check for "Left" or "Right" diagonals (exclusive)
            elif x_rel < y_rel + 1 and x_rel < -y_rel + 1:
                return 3
            elif x_rel > y_rel - 1 and x_rel > -y_rel - 1:
                return 1
    
    def hori_move(self):
        if pyxel.btn(pyxel.KEY_A):
            if self.gdirection == 0:
                self.xv -= self.speed
            if self.gdirection == 1:
                self.yv -= self.speed
            if self.gdirection == 2:
                self.xv += self.speed
            if self.gdirection == 3:
                self.yv += self.speed
        
        if pyxel.btn(pyxel.KEY_D):
            if self.gdirection == 0:
                self.xv += self.speed
            if self.gdirection == 1:
                self.yv += self.speed
            if self.gdirection == 2:
                self.xv -= self.speed
            if self.gdirection == 3:
                self.yv -= self.speed
        
        if self.gdirection == 0 or self.gdirection == 2:
            self.xv *= self.friction
            self.x += self.xv

            if self.xv < 0:   
                self.x = pyxel.ceil(self.x)
            else:
                self.x = pyxel.floor(self.x)
        
        elif self.gdirection == 1 or self.gdirection == 3:
            self.yv *= self.friction
            self.y += self.yv

            if self.yv < 0:   
                self.y = pyxel.ceil(self.y)
            else:
                self.y = pyxel.floor(self.y)

    def hori_col(self):
        
        if self.gdirection == 0 or self.gdirection == 2:
            if self.xv > 0: 
                while get_tile((self.x + self.w - 1) // 8, (self.y) // 8, 0) in SOLID or get_tile((self.x + self.w - 1) // 8, (self.y + self.h - 1) // 8, 0) in SOLID:
                    self.xv = 0
                    self.x -= 1
            elif self.xv < 0:
                while get_tile((self.x) // 8, (self.y) // 8, 0) in SOLID or get_tile((self.x) // 8, (self.y + self.h - 1) // 8, 0) in SOLID:
                    self.xv = 0
                    self.x += 1
        
        elif self.gdirection == 1 or self.gdirection == 3:
            if self.yv < 0: 
                while get_tile((self.x) // 8, (self.y) // 8, 0) in SOLID or get_tile((self.x + self.w - 1) // 8, (self.y) // 8, 0) in SOLID:
                    self.yv = 0
                    self.y += 1
            elif self.yv > 0:
                while get_tile((self.x) // 8, (self.y + self.h - 1) // 8, 0) in SOLID or get_tile((self.x + self.w - 1) // 8, (self.y + self.h - 1) // 8, 0) in SOLID:
                    self.yv = 0
                    self.y -= 1

    def vert_move(self):
        # gravity and grounded checks
        if self.gdirection == 0:
            self.yv += self.g
            if self.yv > 1:
                self.grounded = False
        if self.gdirection == 1:
            self.xv -= self.g
            if self.xv < -1:
                self.grounded = False
        if self.gdirection == 2:
            self.yv -= self.g
            if self.yv < -1:
                self.grounded = False
        if self.gdirection == 3:
            self.xv += self.g
            if self.xv > 1:
                self.grounded = False
        
        # jetpack going up
        if pyxel.btn(pyxel.KEY_W):
            if self.fuel > 0:
                if self.gdirection == 0:
                    self.yv += -self.j
                    if self.yv < -3:
                        self.yv = -3
                    
                    ps.emit(self.x + self.w/2, self.y + self.h, count=3, size= 1, gravity=0, color= 8, vy= 0.5, lifespan=7)
                    ps.emit(self.x + self.w/2, self.y + self.h, count=3, size= 1, gravity=0, color= 9, vy= 0.5, lifespan=7)
                
                if self.gdirection == 1:
                    self.xv += self.j
                    if self.xv > 3:
                        self.xv = 3
                    
                    ps.emit(self.x, self.y + self.h/2, count=3, size= 1, gravity=0, color= 8, vx= -0.5, lifespan=7)
                    ps.emit(self.x, self.y + self.h/2, count=3, size= 1, gravity=0, color= 9, vx= -0.5, lifespan=7)
                
                if self.gdirection == 2:
                    self.yv += self.j
                    if self.yv > 3:
                        self.yv = 3
                    
                    ps.emit(self.x + self.w/2, self.y, count=3, size= 1, gravity=0, color= 8, vy= -0.5, lifespan=7)
                    ps.emit(self.x + self.w/2, self.y, count=3, size= 1, gravity=0, color= 9, vy= -0.5, lifespan=7)
                
                if self.gdirection == 3:
                    self.xv += -self.j
                    if self.xv < -3:
                        self.xv = -3
                    
                    ps.emit(self.x + self.w, self.y + self.h/2, count=3, size= 1, gravity=0, color= 8, vx= 0.5, lifespan=7)
                    ps.emit(self.x + self.w, self.y + self.h/2, count=3, size= 1, gravity=0, color= 9, vx= 0.5, lifespan=7)
                
                self.fuel -= 1
            
            self.grounded = False
        
        if self.gdirection == 1 or self.gdirection == 3:
            self.x += self.xv

            if self.xv < 0:
                self.x = pyxel.ceil(self.x)
            else:
                self.x = pyxel.floor(self.x)
        
        elif self.gdirection == 0 or self.gdirection == 2:
            self.y += self.yv

            if self.yv < 0:   
                self.y = pyxel.ceil(self.y)
            else:
                self.y = pyxel.floor(self.y)

    def vert_col(self):
        self.just_grounded = False
        
        if self.gdirection == 1 or self.gdirection == 3:
            if self.xv > 0:
                while get_tile((self.x + self.w - 1) // 8, (self.y) // 8, 0) in SOLID or get_tile((self.x + self.w - 1) // 8, (self.y + self.h - 1) // 8, 0) in SOLID:
                    if self.gdirection == 3:
                        self.grounded = True
                        if self.xv > 1:
                            self.just_grounded = True
                    self.xv = 0
                    self.x -= 1
            
            elif self.xv < 0:
                while get_tile((self.x) // 8, (self.y) // 8, 0) in SOLID or get_tile((self.x) // 8, (self.y + self.h - 1) // 8, 0) in SOLID:
                    if self.gdirection == 1:
                        self.grounded = True
                        if self.xv < -1:
                            self.just_grounded = True
                    self.xv = 0
                    self.x += 1
        
        elif self.gdirection == 0 or self.gdirection == 2:
            if self.yv < 0: 
                while get_tile((self.x) // 8, (self.y) // 8, 0) in SOLID or get_tile((self.x + self.w - 1) // 8, (self.y) // 8, 0) in SOLID:
                    if self.gdirection == 2:
                        self.grounded = True
                        if self.yv < -1:
                            self.just_grounded = True
                    self.yv = 0
                    self.y += 1

            elif self.yv > 0:
                while get_tile((self.x) // 8, (self.y + self.h - 1) // 8, 0) in SOLID or get_tile((self.x + self.w - 1) // 8, (self.y + self.h - 1) // 8, 0) in SOLID:
                    if self.gdirection == 0:
                        self.grounded = True
                        if self.yv > 1:
                            self.just_grounded = True
                    self.yv = 0
                    self.y -= 1
    
    def ship_move(self):
        ######## rotational update ###########
        if pyxel.btn(pyxel.KEY_A):
            self.rov -= 1
        if pyxel.btn(pyxel.KEY_D):
            self.rov += 1
        
        self.rov *= self.friction
        
        self.ro += self.rov
        
        ######## x and y update ############
        if self.fuel > 0:
            if pyxel.btn(pyxel.KEY_W):
                self.f += self.fspeed
                self.fuel -= 1
                
                # flames emition
                dx = pyxel.cos(self.ro - 90) * -2
                dy = pyxel.sin(self.ro - 90) * -2

                for blah in range(2):
                    ps.emit(self.x + self.w/2, self.y+ self.h/2 , count=1, size= 1, gravity=0, color= 8, vx= dx+random.random()*2 - 1, vy= dy+random.random()*2 - 1, lifespan=7)
                    ps.emit(self.x + self.w/2, self.y+ self.h/2 , count=1, size= 1, gravity=0, color= 9, vx= dx+random.random()*2 - 1, vy= dy+random.random()*2 - 1, lifespan=7)
            
            if pyxel.btn(pyxel.KEY_S):
                self.f -= self.fspeed
                self.fuel -= 1

                # flames emition
                dx = pyxel.cos(self.ro - 90) * 2
                dy = pyxel.sin(self.ro - 90) * 2

                for blah in range(2):
                    ps.emit(self.x + self.w/2, self.y+ self.h/2 , count=1, size= 1, gravity=0, color= 8, vx= dx+random.random()*2 - 1, vy= dy+random.random()*2 - 1, lifespan=7)
                    ps.emit(self.x + self.w/2, self.y+ self.h/2 , count=1, size= 1, gravity=0, color= 9, vx= dx+random.random()*2 - 1, vy= dy+random.random()*2 - 1, lifespan=7)
        
        self.f *= 0.9

        # converts f to x and y
        self.xv = pyxel.cos(self.ro - 90) * self.f
        self.yv = pyxel.sin(self.ro - 90) * self.f

        self.x += self.xv
        self.y += self.yv
    
    def ship_col(self):
        # if you touch any obstacles then you die and restart like when you run out of fuel
        if get_tile((self.x+self.w/2) // 8, (self.y+self.h/2) // 8, 0) in SOLID or get_tile((self.x+self.w/2) // 8, (self.y+self.h/2) // 8, 0) in SOLID:
            self.fuel = 0
            self.visible = False
            for i in range(30):
                ps.emit(self.x + self.w/2, self.y + self.h, count=1, size= 5, gravity=0, color= 8, lifespan=30, vy=random.randint(-3, 3) * random.random(), vx=random.randint(-3, 3) * random.random())
        
        # limits
        if self.x < 0:
            self.x = 0
            self.xv = 0
        if self.x > 2040:
            self.x = 2040
            self.xv = 0
        if self.y < 0:
            self.y = 0
            self.yv = 0
        if self.y > 2040:
            self.y = 2040
            self.yv = 0

    def visual(self):
        if self.gravitational:    
            if self.gdirection == 0:
                self.ro = 0
            if self.gdirection == 1:
                self.ro = 90
            if self.gdirection == 2:
                self.ro = 180
            if self.gdirection == 3:
                self.ro = 270
            
        else:
            self.direction_x = 1
            self.direction_y = 1
            pass
        
        self.ro = self.ro % 360
        self.ro = round(self.ro)
        #applies rotation backwards becasue the player is the view
        self.dro = self.ro * -1

        def update_frame():
            self.frame_count += 1
            if self.frame_count > self.max_frame_count:
                self.frame_count = 0
            if self.frame_count == 1:
                self.frame += 1
            
            if self.frame > self.max_frame:
                self.frame = 0

        if self.gravitational:
            # Animation
            if self.gdirection == 0 or self.gdirection == 2:
                if round(self.xv * 0.5) != 0:
                    update_frame()
                else:
                    self.frame = 0
            elif self.gdirection == 1 or self.gdirection == 3:
                if round(self.yv * 0.5) != 0:
                    update_frame()
                else:
                    self.frame = 0
            
            # when flying
            if not self.grounded and self.fuel > 0:
                self.frame = 4
            
            # direction facing
            if self.gdirection == 0:
                self.direction_y = 1
                if self.xv > 0:
                    self.direction_x = 1
                if self.xv < 0:
                    self.direction_x = -1
            if self.gdirection == 1:
                self.direction_x = 1
                if self.yv > 0:
                    self.direction_y = 1
                if self.yv < 0:
                    self.direction_y = -1
            if self.gdirection == 2:
                self.direction_y = 1
                if self.xv > 0:
                    self.direction_x = -1
                if self.xv < 0:
                    self.direction_x = 1
            if self.gdirection == 3:
                self.direction_x = 1
                if self.yv > 0:
                    self.direction_y = -1
                if self.yv < 0:
                    self.direction_y = 1
        else:
            self.frame = 4
        
        if self.just_grounded:
            self.frame = 5
            if self.gdirection == 0:
                for blah in range(5):
                    ps.emit(self.x + self.w/2, self.y+ self.h, count=1, size= 1, gravity=0, color= 7, vx=random.random() - 0.5, vy=random.random() - 0.5, lifespan=10)
            if self.gdirection == 1:
                for blah in range(5):
                    ps.emit(self.x, self.y + self.h/2, count=1, size= 1, gravity=0, color= 7, vx=random.random() - 0.5, vy=random.random() - 0.5, lifespan=10)
            if self.gdirection == 2:
                for blah in range(5):
                    ps.emit(self.x + self.w/2, self.y, count=1, size= 1, gravity=0, color= 7, vx=random.random() - 0.5, vy=random.random() - 0.5, lifespan=10)
            if self.gdirection == 3:
                for blah in range(5):
                    ps.emit(self.x + self.w, self.y+ self.h/2, count=1, size= 1, gravity=0, color= 7, vx=random.random() - 0.5, vy=random.random() - 0.5, lifespan=10)

        thrust = pyxel.btn(pyxel.KEY_W)  # hold UP to thrust
        thrust2 = pyxel.btn(pyxel.KEY_S) and not self.gravitational
        # Channel 0 = sound priority: thruster > mining

        # THRUSTER
        if thrust:  # or whatever flag you use for thrust
            if pyxel.play_pos(0) is None:
                pyxel.play(0, 0, loop=True)  # thruster loop
            # stop mining sound if it was playing
            self.mining = False
        elif thrust2:
            if pyxel.play_pos(0) is None:
                pyxel.play(0, 0, loop=True)  # thruster loop
            # stop mining sound if it was playing
            self.mining = False
        
        # MINING (only if not thrusting)
        elif self.mining:
            if not is_colliding_with_tile(self.x, self.y, self.w, self.h, SHOPPING_TILES, 0):
                if pyxel.play_pos(0) is None:
                    pyxel.play(0, 1, loop=True)  # mining loop

        # NO ACTION
        else:
            pyxel.stop(0)
        
        # BROKE BLOCK
        if self.broke:
            pyxel.play(0, 2, loop=False)  # mining loop
    
    def mineplace(self):
        # sets mining d to gravity d.
        self.mining_d = self.gdirection
        
        # adds mining d to gravity d with key press
        if pyxel.btn(pyxel.KEY_UP):
            self.mining_d += 1
        
        elif pyxel.btn(pyxel.KEY_RIGHT):
            self.mining_d += 2
        
        elif pyxel.btn(pyxel.KEY_DOWN):
            self.mining_d += 3
        
        elif pyxel.btn(pyxel.KEY_LEFT):
            self.mining_d += 4
        
        else:
            self.mining_d = 0

        if self.mining_d > 4:
            self.mining_d -= 4
        
        # sets where the mining x and y is
        if self.mining_d == 1:
            self.mining_x = round(self.x / 8) * 8
            self.mining_y = pyxel.floor((self.y - 8) / 8) * 8
        
        elif self.mining_d == 2:
            self.mining_x = pyxel.ceil((self.x + 8) / 8) * 8
            self.mining_y = round(self.y / 8) * 8
        
        elif self.mining_d == 3:
            self.mining_x = round(self.x / 8) * 8
            self.mining_y = pyxel.ceil((self.y + 8) / 8) * 8
        
        elif self.mining_d == 4:
            self.mining_x = pyxel.floor((self.x - 8) / 8) * 8
            self.mining_y = round(self.y / 8) * 8
        
        # can't mine in space
        if not self.gravitational:
            self.mining_d = 0
        
        # which tile is being mined
        self.tile_s = get_tile(self.mining_x // 8, self.mining_y // 8, 0)

        # # only mine solid tiles
        # if self.tile_s in SOLID:
        #     # when any mining keys pressed
        #     if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_UP):
        #         # set mining time
        #         if pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.KEY_UP) or (self.old_mining_x != self.mining_x or self.old_mining_y != self.mining_y):
        #             self.mining_t = 30 * MINE_T[SOLID.index(self.tile_s)]
        #         else:
        #             self.mining_t -= self.mining_speed
        #             if self.mining_t <= 0:
        #                 pyxel.tilemaps[0].pset(self.mining_x // 8, self.mining_y // 8, (0, 0))
        #                 # adds item to backpack when mined
        #                 if len(self.backpack) < self.capacity:    
        #                     self.backpack.append(SOLID.index(self.tile_s))
        #                 else:
        #                     notification_manager.add("Backpack Full", 120, 112)
        #                 self.mining_t = -1
        # else: 
        #     self.mining_t = -1

        # only mine solid tiles
        # this used for sounds
        self.broke = False

        if self.tile_s in SOLID:
            if (pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_LEFT) or
                pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_UP)):

                if (pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_LEFT) or
                    pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.KEY_UP) or
                    (self.old_mining_x != self.mining_x or self.old_mining_y != self.mining_y)):

                    self.mining_t = 30 * MINE_T[SOLID.index(self.tile_s)]

                else:
                    self.mining_t -= self.mining_speed
                    self.mining = True
                    if self.mining_t <= 0:
                        pyxel.tilemaps[0].pset(self.mining_x // 8, self.mining_y // 8, (0, 0))
                        if len(self.backpack) < self.capacity:    
                            self.backpack.append(SOLID.index(self.tile_s))
                            self.broke = True
                        else:
                            notification_manager.add("Backpack Full", 120, 112)
                        self.mining_t = -1
                        self.mining = False

            else:
                self.mining_t = -1
                self.mining = False
        else: 
            self.mining_t = -1
            self.mining = False



        self.old_mining_x = self.mining_x
        self.old_mining_y = self.mining_y
    
        # this is to find the nearest planet to the player
    def get_nearest_planet(self, x, y):
        nearest = None
        min_dist = float('inf')

        for planet in range (len(planets)):
            dx = planets[planet].x - x
            dy = planets[planet].y - y
            dist = (dx ** 2 + dy ** 2) ** 0.5

            if dist < min_dist:
                min_dist = dist
                nearest = planet

        self.nearest_planet_index = nearest
    
    def buy_sell(self):
        # selling
        if is_colliding_with_tile(self.x + 1, self.y, self.w - 2, self.h, [(0, 7)], 0):
            if not pyxel.btn(pyxel.KEY_DOWN):
                self.show_downkey = True
            else:
                self.show_downkey = False
            
            if pyxel.btnp(pyxel.KEY_DOWN) and len(self.backpack) > 0:
                # sell
                count = 0
                for i in self.backpack:
                    self.money += PRICES[i]
                    count += PRICES[i]

                notification_manager.add("+ $" + str(count), 120, 112)
                pyxel.stop(0)
                pyxel.play(0, 3, loop=False)
                self.backpack = []

        # pickaxe upgrade
        elif is_colliding_with_tile(self.x + 1, self.y, self.w - 2, self.h, [(1, 7)], 0):
            if not pyxel.btn(pyxel.KEY_DOWN):
                self.show_downkey = True
            else:
                self.show_downkey = False
            
            if pyxel.btnp(pyxel.KEY_DOWN) and self.money >= self.price_of_pick:
                self.money -= self.price_of_pick
                self.mining_speed += 1
                notification_manager.add("+1 mining speed", 120, 112)
                pyxel.stop(0)
                pyxel.play(0, 4, loop=False)
                self.price_of_pick += self.price_of_pick

        
        # fuel upgrade
        elif is_colliding_with_tile(self.x + 1, self.y, self.w - 2, self.h, [(2, 7)], 0):
            if not pyxel.btn(pyxel.KEY_DOWN):
                self.show_downkey = True
            else:
                self.show_downkey = False
            
            if pyxel.btnp(pyxel.KEY_DOWN) and self.money >= self.price_of_fuel:
                self.money -= self.price_of_fuel
                self.fuel_cap += self.fuel_cap / 2
                notification_manager.add("+1 fuel capacity", 120, 112)
                pyxel.stop(0)
                pyxel.play(0, 4, loop=False)
                self.fuel_cap = int(self.fuel_cap)
                self.price_of_fuel += self.price_of_fuel
        
        # capacity upgrade
        elif is_colliding_with_tile(self.x + 1, self.y, self.w - 2, self.h, [(3, 7)], 0):
            if not pyxel.btn(pyxel.KEY_DOWN):
                self.show_downkey = True
            else:
                self.show_downkey = False
            
            if pyxel.btnp(pyxel.KEY_DOWN) and self.money >= self.price_of_cap:
                self.money -= self.price_of_cap
                self.capacity += 20
                notification_manager.add("+1 backpack capacity", 120, 112)
                pyxel.stop(0)
                pyxel.play(0, 4, loop=False)
                self.price_of_cap += self.price_of_cap
        
        # HyperDrive # END OF THE GAME ########################################
        elif is_colliding_with_tile(self.x + 1, self.y, self.w - 2, self.h, HYPER_DRIVE, 0):
            if not pyxel.btn(pyxel.KEY_DOWN):
                self.show_downkey = True
            else:
                self.show_downkey = False
            
            if pyxel.btnp(pyxel.KEY_DOWN) and self.money >= 200000:
                self.money -= 200000
                self.game_fin = True
                pyxel.stop()
        
        else:
            self.show_downkey = False

    def update(self):
        if self.planet_counter == 0:
            self.planet_x = 0
            self.planet_y = 0
        
        self.old_gravitational = self.gravitational

        if self.planet_x > 0 and self.planet_y > 0:
            self.gravitational = True
        else:
            self.gravitational = False
        
        # if no planet, ship updates
        if self.gravitational:
            self.f = 0

            # sets gravity direction
            self.gdirection = self.get_gravity(self.x + self.w/2, self.y + self.h/2, self.planet_x, self.planet_y)
        
            # calcualtes the horizontal movement, then colision, same with vertical
            # horizontal and vertical are relative to the planets gravity on player
            if self.dead == False:
                self.hori_move()
                self.hori_col()
                self.vert_move()
                self.vert_col()

        else:
            # if theres no planet the player is in the atmosphere of, g = 0 default
            self.gdirection = 0
            if self.dead == False:
                self.ship_move()
                self.ship_col()
        
        self.old_mining = self.mining
        self.mineplace()

        self.get_nearest_planet(self.x, self.y)

        # fuel full if in home planet
        if self.nearest_planet_index == 0 and self.gravitational and self.dead == False:
            self.fuel = self.fuel_cap
            if self.old_gravitational != self.gravitational:
                notification_manager.add("Refueled", 120, 112)
        
        self.visual()

        self.buy_sell()

        if self.fuel <= 0:
            self.dead = True
            self.frame = 4
            if pyxel.btnp(pyxel.KEY_Z):
                self.yv = 0
                self.xv = 0
                self.x = 120 + 256
                self.y = 64 + 256
                self.backpack = []
                self.visible = True
                self.dead = False

    def draw(self):
        if self.visible:
            pyxel.blt(self.x, self.y, 0, 0 + (self.w * self.frame), 8, self.w * self.direction_x, self.h * self.direction_y, 14, self.dro * -1, self.sc)
        
        # mining cursor
        if not is_colliding_with_tile(self.x, self.y, self.w, self.h, SHOPPING_TILES, 0):    
            if self.mining_d != 0:
                pyxel.rectb(self.mining_x - 1, self.mining_y - 1, 10, 10, 7)
                if self.tile_s in SOLID:
                    frame = min(1 + int(((1 - (self.mining_t / (30 * MINE_T[SOLID.index(self.tile_s)]))) * 4)), 5)
                else: 
                    frame = 0
                pyxel.blt(self.mining_x, self.mining_y, 0, 0 + (frame * 8), 16, 8, 8, 14)
        
        if self.show_downkey:
            pyxel.blt(player.x, player.y - 12, 0, 8, 64, 8, 8, 14)

        # prices
        
        # fuel capacity upgrade
        if self.money >= self.price_of_fuel:
            c = 11
        else:
            c = 8
        draw_text_with_outline(94 + 256, 89 + 256, "$"+str(self.price_of_fuel), c, 0)
        # sell
        draw_text_with_outline(110 + 256, 81 + 256, "SELL", 11, 0)
        # pickaxe upgrade
        if self.money >= self.price_of_pick:
            c = 11
        else:
            c = 8
        draw_text_with_outline(126 + 256, 89 + 256, "$"+str(self.price_of_pick), c, 0)
        # capacity upgrade
        if self.money >= self.price_of_cap:
            c = 11
        else:
            c = 8
        draw_text_with_outline(142 + 256, 81 + 256, "$"+str(self.price_of_cap), c, 0)
        # hyperdrive upgrade
        if self.money >= 200000:
            c = 11
        else:
            c = 8
        draw_text_with_outline(114 + 256, 50 + 256, "$200000", c, 0)

class Inventory:
    def __init__(self):
        self.tile_size = 8
        self.inventory_cols = 5
        self.padding = 5
        self.font_color = 7  # White
        self.width = 128
        self.height = 128

    def update(self):
        pass

    def draw(self):
        
        # Count duplicates
        self.tile_counter = Counter(player.backpack)

        x_start = self.padding + camera.x
        y_start = self.padding + camera.y + 120
        i = 0

        for tile_index, count in self.tile_counter.items():
            if tile_index >= len(SOLID):
                continue
            
            tile_x, tile_y = SOLID[tile_index]

            col = i % self.inventory_cols
            row = i // self.inventory_cols

            x = x_start + col * (self.tile_size + self.padding)
            y = y_start + row * (self.tile_size + self.padding)

            pyxel.blt(
                x, y,
                img=0,
                u=tile_x * self.tile_size,
                v=tile_y * self.tile_size,
                w=self.tile_size,
                h=self.tile_size,
                colkey=14
            )
            pyxel.rectb(x-1,y-1,self.tile_size+2,self.tile_size+2,0)

            if count > 1:
                draw_text_with_outline(x + 4, y + 4, str(count), self.font_color, 0)

            i += 1

class Notification:
    def __init__(self, text, x, y, duration=60):
        self.text = text
        self.x = x
        self.y = y
        self.duration = duration
        self.age = 0

    def update(self):
        self.age += 1
        self.y -= 0.3  # Move upward slightly

    def is_expired(self):
        return self.age >= self.duration

    def draw(self):
        alpha = max(0, (self.duration - self.age) / self.duration)
        color = 7 if alpha > 0.5 else 6 if alpha > 0.2 else 5
        pyxel.text(int(self.x) + camera.x, int(self.y) + camera.y, self.text, color)

class NotificationManager:
    def __init__(self):
        self.notifications = []

    def add(self, text, x=60, y=80, duration=60):
        self.notifications.append(Notification(text, x, y, duration))

    def update(self):
        for n in self.notifications:
            n.update()
        self.notifications = [n for n in self.notifications if not n.is_expired()]

    def draw(self):
        for n in self.notifications:
            n.draw()

class Planet:
    def __init__(self, x, y, r):
        self.x = x * 8
        self.y = y * 8
        self.r = r * 8 # radius, but its a square
        self.w = self.r * 2
        self.h = self.r * 2

    def update(self):
        # see if player is colliding with atmosphere, calculated from center of player,
        if is_colliding(self.x - self.r, player.x + player.w/2, self.y - self.r, player.y + player.h/2, self.w, 0, self.h, 0):
            player.planet_x = self.x
            player.planet_y = self.y
            player.planet_counter += 1
    
    def draw(self):
        pyxel.rectb(self.x - self.r, self.y - self.r, self.w, self.h, 7)

class Env:
    def __init__(self):
        pass

    def update(self):
        pass
    
    def draw(self):
        # planets.append(Planet(48, 48, 12))
        # planets.append(Planet(208, 48, 16))
        # planets.append(Planet(128, 128, 32))
        # planets.append(Planet(56, 200, 24))
        # planets.append(Planet(200, 200, 24))
        # planets.append(Planet(36, 116, 4))
        
        pyxel.rect(36*8, 36*8, 24*8, 24*8, 12)
        
        pyxel.rect(192*8, 32*8, 32*8, 32*8, 12)
        
        pyxel.rect(96*8, 96*8, 64*8, 64*8, 1)
        pyxel.dither(0.8)
        pyxel.rect(96*8, 96*8, 64*8, 64*8, 12)
        pyxel.dither(1.0)
        
        pyxel.rect(32*8, 176*8, 48*8, 48*8, 12)
        
        pyxel.rect(176*8, 176*8, 48*8, 48*8, 2)
        pyxel.dither(0.8)
        pyxel.rect(176*8, 176*8, 48*8, 48*8, 1)
        pyxel.dither(1.0)

class App:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Gravitore", fps=30, display_scale=3)
        pyxel.load("assets.pyxres")
        
        pyxel.colors.from_list([
            0x000000,
            0x1D2B53,
            0x7E2553,
            0x008751,
            0xAB5236,
            0x5F574F,
            0xC2C3C7,
            0xFFF1E8,
            0xFF004D,
            0xFFA300,
            0xFFEC27,
            0x00E436,
            0x29ADFF,
            0x7E7E7E,
            0xFF77A8,
            0xEBB896
        ])

        # pyxel.colors[5] = 0x5F574F
        # pyxel.colors[6] = 0xC2C3C7
        # pyxel.colors[12] = 0x29ADFF

        global notification_manager
        notification_manager = NotificationManager()
        
        global player
        player = Player()

        global camera
        camera = Camera()

        global env
        env = Env()

        global ps
        ps = ParticleSystem()

        global inventory
        inventory = Inventory()

        self.notifications = []

        self.state = "TITLE"
        pyxel.playm(0, loop=True)
        self.fin_count = 0
        self.c_size = 0
        self.c_vs = 0
        self.rocket_y = 0
        self.rocket_yv = 0
        self.thanks_color = 0

        self.tut = False

        append_objects()

        pyxel.run(self.update, self.draw)

    def rotate_screen(self, angle_deg):
        # create 256 x 256 matrix
        matrix = [""] * SCREEN_HEIGHT
        # copy data onto matrix
        for y in range(SCREEN_HEIGHT):
            for x in range(SCREEN_WIDTH):
                color = convert_color(pyxel.pget(x, y))
                # need this to be string because setting image only works with lists of strings
                matrix[y] += str(color)

        pyxel.images[1].set(0, 0, matrix)

        pyxel.blt(camera.x, camera.y, 1, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 14, angle_deg, camera.zoom)

    def update(self):
        if self.state == "PLAYING":
            self.update_game()
        elif self.state == "FIN":
            self.update_game_over()
        elif self.state == "TITLE":
            self.update_title()
        
        # if pyxel.btnp(pyxel.KEY_SPACE):
        #     print(str(pyxel.mouse_x) +" "+ str(pyxel.mouse_y))

    def update_game(self):
        env.update()
        
        player.planet_counter = 0
        for planet in planets:
            planet.update()
        
        player.update()

        camera.update()

        ps.update()

        notification_manager.update()

        if player.game_fin:
            self.state = "FIN"
            player.mining_d = 0
            player.frame = 0
            player.x = 380
            player.y = 296
            pyxel.playm(0, loop=True)
    
    def update_game_over(self):
        self.fin_count += 1
        
        if self.fin_count < 30:
            self.c_vs += 1
            self.c_size += self.c_vs
            self.rocket_y = 256
        if self.fin_count > 30 and self.fin_count < 90:
            self.rocket_yv -= 0.1

        self.rocket_yv = self.rocket_yv * 0.95
        self.rocket_y += self.rocket_yv

        for blah in range(5):    
            dx = random.randint(-3, 3)
            dy = random.randint(3, 10)
            ps.emit(camera.x + 128, self.rocket_y + camera.y + 26, count=1, size= 6, gravity=0, color= 1, vx=dx, vy=dy, lifespan=10)
            ps.emit(camera.x + 128, self.rocket_y + camera.y + 26, count=1, size= 4, gravity=0, color= 12, vx=dx, vy=dy, lifespan=10)
            ps.emit(camera.x + 128, self.rocket_y + camera.y + 26, count=1, size= 3, gravity=0, color= 7, vx=dx, vy=dy, lifespan=10)
        
        if self.fin_count > 0:    
            self.thanks_color = 0
        if self.fin_count > 60:
            self.thanks_color = 1
        if self.fin_count > 75:
            self.thanks_color = 5
        if self.fin_count > 90:
            self.thanks_color = 13
        if self.fin_count > 105:
            self.thanks_color = 6
        if self.fin_count > 120:
            self.thanks_color = 7
        
        env.update()
        camera.update()
        ps.update()
        ######### game over cutscene then polish entire game!!!! ###############################################################################################################
    def update_title(self):
        if self.tut:    
            if pyxel.btnp(pyxel.KEY_DOWN):
                self.state = "PLAYING"
                pyxel.stop()
                pyxel.playm(1, loop=True)
        else:
            if pyxel.btnp(pyxel.KEY_DOWN):
                self.tut = True

    def draw(self):
        pyxel.cls(0) # Clear screen

        pyxel.camera(camera.x, camera.y)

        # draw env
        env.draw()
        
        # Draw Tilemap
        pyxel.bltm(0, 0, 0, 0, 0, 256 * 8, 256 * 8, 14, 0, 1)

        # draws atmosphere
        for planet in planets:
            planet.draw()
        
        # particles
        ps.draw()
        
        # Draw player
        player.draw()

        #### ROTATES THE SCREEN #### anything after this isn't displayed rotated
        self.rotate_screen(camera.ro * -1)

        draw_circle_mask()

        notification_manager.draw()

        # mouse cursor
        pyxel.pset(pyxel.mouse_x + camera.x, pyxel.mouse_y+camera.y, 0)
        pyxel.rectb(pyxel.mouse_x - 1 + camera.x, pyxel.mouse_y - 1+camera.y, 3, 3, 7)
        
        pyxel.text(camera.x + 4, camera.y + 18, str(len(player.backpack)) + "/" + str(player.capacity), 7)
        draw_text_with_outline(camera.x + 4, camera.y + 4, "$"+str(player.money), 11, 0)
        pyxel.rect(camera.x + 4, camera.y + 11, int(50 * player.fuel / player.fuel_cap), 5, 8)
        pyxel.rectb(camera.x + 3, camera.y + 10, 52, 7, 7)
        if player.nearest_planet_index == 0 and player.gravitational:
            pyxel.rect(camera.x + 4, camera.y + 11, 50, 5, 8)

        if player.dead:
            pyxel.rect(camera.x + 99, camera.y + 163, 73, 7, 0)
            pyxel.text(camera.x + 100, camera.y + 164, "PRESS Z TO RESPAWN", 7)

        # minimap
        
        # make it black and white
        pyxel.pal(1, 7)
        pyxel.pal(2, 7)
        pyxel.pal(3, 7)
        pyxel.pal(4, 7)
        pyxel.pal(5, 7)
        pyxel.pal(6, 7)
        pyxel.pal(8, 7)
        pyxel.pal(9, 7)
        pyxel.pal(10, 7)
        pyxel.pal(11, 7)
        pyxel.pal(12, 7)
        pyxel.pal(13, 7)
        pyxel.pal(14, 7)
        pyxel.pal(15, 7)

        pyxel.rect(camera.x + 4, camera.y + 188, 64, 64, 0)
        # pyxel.bltm(camera.x - 220, camera.y - 36, 0, camera.x - 128, camera.y - 128, 512, 512, 14, scale= 0.125)
        pyxel.bltm(camera.x - 92, camera.y + 92, 1, 0, 256, 256, 256, 14, scale= 0.25)
        pyxel.rectb(camera.x + 3, camera.y + 187, 66, 66, 0)

        pyxel.pal()
        # player on map
        pyxel.circ(camera.x + (round(player.x) / 32) + 4, camera.y + (round(player.y) / 32) + 188, 1, 8)

        # end of game cutscene draws
        if player.game_fin:
            # black circle
            pyxel.circ(128 + camera.x, 128 + camera.y, self.c_size, 0)

            # particles
            ps.draw()

            # player rocket
            pyxel.blt(120 + camera.x, camera.y + self.rocket_y, 0, 16, 88, 16, 32, 14)

            # thanks text
            pyxel.text(90+camera.x, 80+camera.y, "THANKS FOR PLAYING", self.thanks_color)
        
        # player inventory
        inventory.draw()

        # TITLE DRAW
        if self.state == "TITLE":
            pyxel.cls(0)
            if self.tut == False:    
                pyxel.blt(56, 64, 0, 0, 240, 9*16, 16, 0)
                pyxel.bltm(0, 0, 1, 0, 0, 256, 256, 14)
                pyxel.text(90, 226, "Made by LANCE REEVE", 7)
                pyxel.text(77, 100, "PRESS DOWN ARROW TO START", 7)
            else:
                pyxel.text(4, 4, "Welcome to GRAVITORE", 7)
                pyxel.text(4, 20, "You've been marooned in an unknown star system.", 7)
                pyxel.text(4, 36, "Your goal is to mine, sell, and upgrade until you", 7)
                pyxel.text(4, 44, "raise enough money to buy a hyperdrive and escape.", 7)
                pyxel.text(4, 60, "Use WASD to move and the arrow keys to mine.", 7)
                pyxel.text(4, 76, "Ore is more valuable than other materials, and the", 7)
                pyxel.text(4, 84, "materials get more valubale the farther you go", 7)
                pyxel.text(4, 100, "Press down to sell and buy while in the shop", 7)
                pyxel.text(4, 116, "Use your jetpack and fuel to travel to other planets but don't", 7)
                pyxel.text(4, 124, "let it run out while you're away or you'll lose your items", 7)
                pyxel.text(4, 140, "Use the minimap to navigate the star system", 7)
                pyxel.text(4, 156, "Good luck!", 7)
                pyxel.text(4, 247, "PRESS DOWN ARROW TO START", 7)

# Run the game
App()
