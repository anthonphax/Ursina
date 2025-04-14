from ursina import *
import math
import random

app = Ursina(size=(430, 932), borderless=True)

planet = Entity(model = 'sphere', scale=.5, texture='assets/Models/deathstart/texture.jpg', position=Vec3(0,0,0), z=1) 

score = 0

btn_right = Button(
    text='  ', 
    parent=camera.ui, 
    model='cube_uv_top', 
    scale=.15, 
    radius=.2, 
    origin=(-0.5,3.3),
    text_colors=color.black, 
    text_origin=(0,0), 
    text_size=2, 
    color=Default, 
    collider='box',
    pressed_scale=0.6)

btn_left = Button(
    text='  ', 
    parent=camera.ui, 
    model='cube_uv_top', 
    scale=.15, 
    radius=.2, 
    origin=(0.5,3.3), 
    text_colors=color.black, 
    text_origin=(0,0), 
    text_size=2, 
    collider='box',
    pressed_scale=0.6)

background = Entity(
    model='quad',
    scale=(4 * camera.aspect_ratio, 6),
    position=Vec3(0, 0),
    texture='./assets/Interface/estrelas.mp4',
    z=2
)

background.always_on_top = False
background.parent = scene

class Player(Entity):
    def __init__(self, radius=1.5, angle=-1.55, speed=1, rotation_speed=0.05):
        super().__init__(
            model='quad',
            color=color.azure,
            scale=0.15,
            z=0
        )
        self.radius = radius
        self.angle = angle
        self.speed = speed
        self.rotation_speed = rotation_speed
        self.update_position()

    def update_position(self):
        self.x = math.cos(self.angle) * self.radius
        self.y = math.sin(self.angle) * self.radius

        # Limites da tela
        max_x = camera.aspect_ratio * 1.6
        max_y = 1.8
        self.x = clamp(self.x, -max_x, max_x)
        self.y = clamp(self.y, -max_y, max_y)

    def update(self):
        self.update_position()

        if btn_left.hovered and mouse.left:
            player.rotate('left')
            rotate_around_point_2d(player.position, player.position, 90)
        
        if btn_right.hovered and mouse.left:
            player.rotate('right')

    def rotate(self, direction):
        if direction == 'right':
            self.angle += 0.05 * self.rotation_speed
            print('right')
        elif direction == 'left':
            self.angle -= 0.05 * self.rotation_speed
            print('left')
        self.update_position()

class Ray(Entity):
    def __init__(self, start_pos, direction):
        super().__init__(
            model='sphere',
            color=color.red,
            scale=(0.02, 0.02),
            position=start_pos,
            collider='box'
        )
        self.velocity = 0
        self.acceleration = 8
        self.direction = direction.normalized()

    def update(self):
        self.velocity += self.acceleration * time.dt
        self.position += self.direction * self.velocity * time.dt

        if distance(self.position, Vec3(0, 0, 0)) < 0.1:
            destroy(self)

class Enemy(Entity):
    def __init__(self, start_pos, direction):
        super().__init__(
            model='assets/Models/saucer/13884_UFO_Saucer_v1_l2.obj',
            scale=0.0005,
            position=start_pos,
            collider='box'
        )
        self.velocity = 0
        self.acceleration = 8
        self.direction = direction.normalized()


    def on_collision(self):
        self.scale *= 1.2 
        score += 10

    def update(self):
        self.velocity += self.acceleration * time.dt
        self.position += self.direction * self.velocity * time.dt

        if distance(self.position, Vec3(0, 0, 0)) > 10:
            destroy(self)

player = Player()
player.level = 1

rays = []
RAY_INTERVAL = 60 / player.level
ray_timer = 0  

enemies = []
ENEMY_INTERVAL = 60 / player.level
enemies_timer = 0  


def update():
    global ray_timer
    global enemies_timer
    global score

    player.update()

    planet.scale += (0.0001, 0.0001, 0.0001)
    
    # Laser
    for ray in rays:
        if ray in scene.entities:
            ray.update()
        ray.ray_time += 1  

    if ray_timer >= RAY_INTERVAL:
        ray_direction = Vec3(0, 0, 0) - player.position
        new_ray = Ray((player.position.x, player.position.y, player.position.z), ray_direction)
        new_ray.ray_time = 0
        rays.append(new_ray)
        ray_timer = 0
    else:
        ray_timer += 1

    # UFOS
    for enemy in enemies:
        if enemy in scene.entities:
            enemy.update()
        enemy.enemies_time += 1  

    if enemies_timer >= ENEMY_INTERVAL:
        enemy_direction = Vec3(0, 0, 0) + player.position
        enemy_position = Vec3(0, 0, 0)
        new_enemy = Enemy(enemy_position, enemy_direction)
        new_enemy.enemies_time = 0
        enemies.append(new_enemy)
        enemies_timer = 0
    else:
        enemies_timer += 1

    hit_info = player.intersects()
    if hit_info.hit:
            print(hit_info.entity)
            score += 10

    print(score)



Sky()
camera.orthographic = True
camera.fov = 4
from ursina.shaders import ssao_shader
camera.shader = ssao_shader
app.run()