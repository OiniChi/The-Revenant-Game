import time
import pygame
from config import *
from settings import *
from levels import *
from ui import UI
from Entity import Entity
import math
import random
from groups import (all_sprites, decorations_group,
                    walls_group, collisions_group, enemy_group,
                    interaсtive_group, player_group)
class Spritesheet:
    def __init__(self, file):
        self.sheet = pygame.image.load(file).convert()

    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface((width, height))

        sprite.blit(self.sheet, (0,0), (x, y, width, height))
        sprite.set_colorkey(BLACK)
        return sprite
class CameraGroup(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
        self.ui = UI()

        # flags
        self.enemy_is_spawned = False
        # Загрузка спрайтов
        self.terrarian_spritesheet = Spritesheet('img/Level_textures/all_sprites.png')
        self.tree_spritesheet = Spritesheet('img/Level_textures/all_sprites.png')
        self.player_spritesheet = Spritesheet('img/Player/Movement/character-export.png')
        self.enemy_spritesheet = Spritesheet('img/Enemy/Movement/character1.png')
        self.chest_spritesheet = Spritesheet('img/Level_textures/all_sprites.png')

        #zoom
        self.zoom_scale = 1
        self.internal_surface_size = (2500, 2500)
        self.internal_surface = pygame.Surface(self.internal_surface_size, pygame.SRCALPHA)
        self.internal_rect = self.internal_surface.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT / 2))
        self.internal_surface_size_vector = pygame.math.Vector2(self.internal_surface_size)
        self.internal_offset = pygame.math.Vector2()
        self.internal_offset.x = self.internal_surface_size[0] // 2 - WIN_WIDTH / 2
        self.internal_offset.y = self.internal_surface_size[1] // 2 - WIN_HEIGHT / 2
        self.enemy_camera_offsetX = 0
        self.enemy_camera_offsetY = 0

        # Генерируем карту
        for i, row in enumerate(tilemap):
            for j, column in enumerate(row):
                if column == "-":
                    Ground(j, i, self.terrarian_spritesheet, 7, 221, 43, 43)
                if column == "+":
                    Ground(j, i, self.terrarian_spritesheet, 59, 221, 43, 43)

        # Генерируем объекты на карте
        for i, row in enumerate(objmap):
            for j, column in enumerate(row):
                if column == "#":
                    Walls(j, i, self.terrarian_spritesheet, 115, 168, 42, 43)
                if column == "%":
                    Walls(j, i, self.terrarian_spritesheet, 7, 168, 43, 42)
                if column == "$":
                    Walls(j, i, self.terrarian_spritesheet, 59, 168, 43, 43)
                if column == ":":
                    Walls(j, i, self.terrarian_spritesheet, 169, 168, 43, 43)
                if column == "1":
                    Walls(j, i, self.terrarian_spritesheet, 15, 367, 43, 43)
                if column == "2":
                    Walls(j, i, self.terrarian_spritesheet, 207, 367, 43, 43)
                if column == "3":
                    Walls(j, i, self.terrarian_spritesheet, 143, 367, 43, 43)
                if column == "4":
                    Walls(j, i, self.terrarian_spritesheet, 79, 367, 43, 43)
                if column == "T":
                    Tree(j, i, self.tree_spritesheet, 433, 1, 185, 193)
                if column == "t":
                    Tree(j, i, self.tree_spritesheet, 250, 1, 167, 197)
                if column == "C":
                    InteractedObjs(j, i, self.chest_spritesheet, 30, 286, 78, 50)
                if column == "P":
                    self.player = Player(j, i, self.player_spritesheet,[all_sprites, decorations_group, collisions_group, player_group],  80, 126)

        # Смещаем камеру(или все спрайты в игре) в цент игрока
        for sprite in all_sprites:  # !!!!!!!!!! ТУТ СМЕЩЕНИЕ КАМЕРА РАБОТАЕТ ТОЛЬКО ВНУТРИ ДИСПЛЕЯ, ЕСТЬ ПРОБЛЕМА СО СПАВНОМ ЗА ЕГО ПРЕДЕЛАМИ(доработать!)
            sprite.rect.x -= WIN_WIDTH - self.player.x + self.player.width if self.player.x > WIN_WIDTH / 2 else -(WIN_WIDTH + self.player.x - self.player.width)
            sprite.rect.y -= WIN_HEIGHT + self.player.y - self.player.height if self.player.y > WIN_WIDTH / 2 else -(WIN_HEIGHT - self.player.y + self.player.height)

        # Запоминаем на какую величину мы сдвинули камеру для корректного спавна Врагов
        self.enemy_camera_offsetX -= WIN_WIDTH - self.player.x + self.player.width
        self.enemy_camera_offsetY -= WIN_HEIGHT - self.player.y + self.player.height
    def spawn_enemies(self):
        hits = pygame.sprite.spritecollide(self.player, interaсtive_group, False)
        if hits and not self.enemy_is_spawned:
            for i, row in enumerate(objmap):
                for j, column in enumerate(row):
                    if column == "e":
                        Enemy('zoombe', j, i, self.enemy_camera_offsetX + self.player.direction.x, self.enemy_camera_offsetY - self.player.direction.y, self.enemy_spritesheet, [all_sprites, enemy_group, decorations_group], 64, 128)
                    if i == len(objmap) - 1 and j == len(row) - 1:
                        self.enemy_is_spawned = True
    def custom_draw(self, player):
        # Перерисовка декоративных объектов для разноплановости
        self.internal_surface.fill('#71ddee')

        for sprite in all_sprites:
            self.offset.x = player.rect.centerx - self.internal_offset.x - WIN_WIDTH / 2
            self.offset.y = player.rect.centery - self.internal_offset.y - WIN_HEIGHT / 2

            floor_offset_pos = sprite.rect.topleft - self.offset
            self.internal_surface.blit(sprite.image, floor_offset_pos)

        for sprite in sorted(decorations_group, key = lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.internal_surface.blit(sprite.image, offset_pos)

        scaled_surf = pygame.transform.scale(self.internal_surface, self.internal_surface_size_vector * self.zoom_scale)
        scaled_rect = scaled_surf.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT / 2))

        all_sprites.update()
        self.display_surface.blit(scaled_surf, scaled_rect)
    def run(self):
        self.custom_draw(self.player)
        self.ui.display(self.player)
        all_sprites.update()
        self.player_update()
        self.enemy_update()
    def gamePaused_info(self):
        return self.ui.game_info()
    def player_update(self):
        for enemy in enemy_group:
            self.player.get_damage(enemy)
    def enemy_update(self):
        for enemy in enemy_group:
            enemy.enemy_update(self.player)
        # return ui.text,
class Player(Entity):
    def __init__(self, x, y, img, groups, width, height):
        self._layer = PLAYER_LAYER
        super().__init__(groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = width
        self.height = height

        player_info = player_data['people']
        self.health = player_info['health']
        self.timers = {
            ''
        }
        # Флаги
        self.attacking = False
        self.can_attack = True
        self.hit_time = 0
        self.is_dead = False
        self.alive_flag = True
        self.is_equipped = False
        self.attack_type = 'weapon'  # В будущем будет None и функция для смены магии и оружия
        self.weapon = None
        self.attack_radius = None
        self.facing = 'down'

        self.animations = {
            'down': [img.get_sprite(0, 0, self.width, self.height),
                     img.get_sprite(80, 0, self.width, self.height),
                     img.get_sprite(160, 0, self.width, self.height),
                     img.get_sprite(240, 0, self.width, self.height)],

            'up': [img.get_sprite(0, 128, self.width, self.height),
                   img.get_sprite(80, 128, self.width, self.height),
                   img.get_sprite(160, 128, self.width, self.height),
                   img.get_sprite(240, 128, self.width, self.height)],

            'right': [img.get_sprite(0, 256, self.width, self.height),
                     img.get_sprite(80, 256, self.width, self.height),
                     img.get_sprite(160, 256, self.width, self.height),
                     img.get_sprite(240, 256, self.width, self.height)],

            'left': [img.get_sprite(0, 384, self.width, self.height),
                      img.get_sprite(80, 384, self.width, self.height),
                      img.get_sprite(160, 384, self.width, self.height),
                      img.get_sprite(240, 384, self.width, self.height)],

            'attack_down': [img.get_sprite(0, 512, self.width, self.height),
                            img.get_sprite(80, 512, self.width, self.height),
                            img.get_sprite(160, 512, self.width, self.height)],

            'attack_up': [img.get_sprite(0, 640, self.width, self.height),
                          img.get_sprite(80, 640, self.width, self.height),
                          img.get_sprite(160, 640, self.width, self.height)],

            'attack_right': [img.get_sprite(0, 768, self.width, self.height),
                            img.get_sprite(80, 768, self.width, self.height),
                            img.get_sprite(160, 768, self.width, self.height)],

            'attack_left': [img.get_sprite(0, 896, self.width, self.height),
                             img.get_sprite(80, 896, self.width, self.height),
                             img.get_sprite(160, 896, self.width, self.height)]
        }
        self.animation_index = 0
        self.directions = {
            pygame.K_a: ('self.direction.x', -PLAYER_SPEED, 'left', 'attack_left'),
            pygame.K_d: ('self.direction.x', PLAYER_SPEED, 'right', 'attack_right'),
            pygame.K_w: ('self.direction.y', -PLAYER_SPEED, 'up', 'attack_up'),
            pygame.K_s: ('self.direction.y', PLAYER_SPEED, 'down', 'attack_down'),
        }
        self.attack_keys = [value[3] for key, value in self.directions.items()]
        self.directions_keys = [value[2] for key, value in self.directions.items()]

        self.image = self.animations['down'][0]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
    def input(self):
        # if not self.attacking:
        keys = pygame.key.get_pressed()

        # attaking input
        if keys[pygame.K_SPACE] and self.is_equipped:
            self.hit_time = pygame.time.get_ticks()
            self.attacking = True

        # movement input
        if keys[pygame.K_w]:
            self.direction.y = -1
            self.facing = 'up'
        elif keys[pygame.K_s]:
            self.direction.y = 1
            self.facing = 'down'
        else:
            self.direction.y = 0

        if keys[pygame.K_d]:
            self.direction.x = 1
            self.facing = 'right'
        elif keys[pygame.K_a]:
            self.direction.x = -1
            self.facing = 'left'
        else:
            self.direction.x = 0
    def get_status(self):
        if self.attacking:
            if not 'attack' in self.facing:
                self.facing = 'attack_' + self.facing
        else:
            if 'attack' in self.facing:
                self.facing = self.facing.replace('attack_', '')
    def animated(self):
        keys = pygame.key.get_pressed()
        current_animation = self.animations[self.facing]
        is_moving = self.direction.x != 0 or self.direction.y != 0

        if self.attacking:
            self.frame_index += self.attack_animation_speed
            # print(self.frame_index)
        else:
            if is_moving:
                self.animation_speed = 0.15 if not keys[PLAYER_KEYS['speed_boost']] else 0.37
                self.frame_index += self.animation_speed
            else:
                self.frame_index = 0

        if self.frame_index >= len(current_animation):
            self.frame_index = 0

        self.image = current_animation[int(self.frame_index)]
        # print(f'facing: {self.facing}, frame:{int(self.frame_index)}')
    # def get_weapon_damage(self, weapon):
    #     return self.weapon[]
    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if self.attacking:
            if current_time - self.hit_time >= int(weapon_data[self.weapon]['cooldown']):
                self.attacking = False
    def get_damage(self, zoombe):
        distance = zoombe.attack_radius
        current_time = pygame.time.get_ticks()
        if distance <= zoombe.attack_radius and zoombe.status == 'attack':
            self.health -= monster_data['zoombe']['damage']
            self.hit_time = pygame.time.get_ticks()

    def check_death(self):
        if self.health <= 0:
            self.kill()
            self.is_dead = True
    def collide_enemy(self):
        # hits = pygame.sprite.spritecollide(self, enemy_group, False)
        #
        # if hits:
        #     self.kill()
        #     playing = False
        pass
    def collide_usebleObj(self):
        hits = pygame.sprite.spritecollide(self, interaсtive_group, False)
        keys = pygame.key.get_pressed()

        if hits and keys[PLAYER_KEYS['usage_key']]:
            self.weapon = hits[0].weapon
            self.attack_radius = weapon_data[self.weapon]['attack_radius']
            self.is_equipped = True

    # Предназначен для обновления состояния игрока на каждом шаге игрового цикла
    def update(self):  # тут будет прописана логика обновления
        keys = pygame.key.get_pressed()
        multiplier = PLAYER_SCORE_COEFF if keys[PLAYER_KEYS['speed_boost']] else 1

        self.input()
        self.cooldowns()
        self.get_status()
        self.animated()
        self.check_death()
        self.movement(PLAYER_SPEED, multiplier)
        self.collide_usebleObj()
        self.collide_enemy()

class Enemy(Entity):
    def __init__(self, monster_name, x, y, i_x, i_y, img, groups, width, height):
        self._layer = PLAYER_LAYER
        self.sprite_type = 'enemy'
        super().__init__(groups)

        # Размер тайла
        # self.dialogue_scr = pygame.image.load('img/Menu/Dilogs/zombe_dialogue.png').convert()
        self.x = x * TILESIZE + i_x
        self.y = y * TILESIZE - i_y
        self.width = width  # Ширина плиты
        self.height = height  # Длинна плиты

        # Графический Статус
        self.img = img
        self.image = self.img.get_sprite(0, 0, 80, 128)

        self.facing = random.choice(['left', 'right'])  # Сторона направления взгляда врага (по умолчанию: 'вниз')
        self.random_key = random.choice(['l_key', 'r_key'])

        self.animation_loop = 0
        self.attack_animation_loop = 0
        self.movement_loop = 0
        self.max_traveling = random.randint(7, 30)
        self.x_change = 0

        # Хитбокс
        self.rect = self.image.get_rect()  # Хитбокс(габариты точки(x,y)) - (Размер спрайта врага = размеру прямоуг.)
        self.rect.x = self.x  # Положение хитбокса = положению  точки врага (по X и Y)
        self.rect.y = self.y

        # stats
        self.status = 'search'
        self.monster_name = monster_name
        monster_info = monster_data[self.monster_name]
        self.health = monster_info['health']
        self.attack_damage = monster_info['damage']
        self.speed = monster_info['speed']
        self.attack_radius = monster_info['attack_radius']
        self.notice_radius = monster_info['notice_radius']

        # timers
        self.hit_time = None
        # Анимации
        self.animations = {
            'down': [img.get_sprite(0, 0, self.width, self.height),
                     img.get_sprite(80, 0, self.width, self.height),
                     img.get_sprite(160, 0, self.width, self.height),
                     img.get_sprite(240, 0, self.width, self.height)],

            'up': [img.get_sprite(0, 128, self.width, self.height),
                   img.get_sprite(80, 128, self.width, self.height),
                   img.get_sprite(160, 128, self.width, self.height),
                   img.get_sprite(240, 128, self.width, self.height)],

            'right': [img.get_sprite(0, 256, self.width, self.height),
                     img.get_sprite(80, 256, self.width, self.height),
                     img.get_sprite(160, 256, self.width, self.height),
                     img.get_sprite(240, 256, self.width, self.height)],

            'left': [img.get_sprite(0, 384, self.width, self.height),
                      img.get_sprite(80, 384, self.width, self.height),
                      img.get_sprite(160, 384, self.width, self.height),
                      img.get_sprite(240, 384, self.width, self.height)],

            'attack_down': [img.get_sprite(0, 512, self.width, self.height),
                            img.get_sprite(80, 512, self.width, self.height),
                            img.get_sprite(160, 512, self.width, self.height)],

            'attack_up': [img.get_sprite(0, 640, self.width, self.height),
                          img.get_sprite(80, 640, self.width, self.height),
                          img.get_sprite(160, 640, self.width, self.height)],

            'attack_right': [img.get_sprite(0, 768, self.width, self.height),
                            img.get_sprite(80, 768, self.width, self.height),
                            img.get_sprite(160, 768, self.width, self.height)],

            'attack_left': [img.get_sprite(0, 896, self.width, self.height),
                             img.get_sprite(80, 896, self.width, self.height),
                             img.get_sprite(160, 896, self.width, self.height)]
        }
    def get_status(self, player):
        distance = self.get_player_distance_direction(player)[0]

        if distance <= self.attack_radius:
            self.status = 'attack'
        elif distance <= self.notice_radius:
            self.status = 'move'
            if round(self.direction.x) != 0:
                self.facing = 'right' if round(self.direction.x) > 0 else 'left'
            else:
                self.facing = 'up' if round(self.direction.y) < 0 else 'down'
        else:
            self.status = 'search'
    def enemy_update(self, player):
        self.get_status(player)
        self.get_damage(player)
        self.actions(player)
    def actions(self, player):
        if self.status == 'attack':
            self.direction = pygame.math.Vector2()
        elif self.status == 'move':
            self.direction = self.get_player_distance_direction(player)[1]
            # print(self.direction.x)
        else:
            # self.direction = pygame.math.Vector2
            # print(f'max_trav_val: {self.max_traveling}, direction.x : {self.direction.x}')
            self.direction.x -= 1 if self.facing == 'left' else -1
            # print(f'max_trav_val: {self.max_traveling}, direction.x : {self.direction.x}')
            self.x_change += int(self.direction.x)
            # print(f'max_trav_val: {self.max_traveling}, x_change: {self.x_change}')
            if abs(self.x_change) >= self.max_traveling:
                # self.direction.x += self.x_change
                self.x_change = 0
                self.direction.y = 0
                self.facing = 'left' if self.facing == 'right' else 'right'
    def get_player_distance_direction(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()  # sqrt(гипотенуза^2) - длина

        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()  # единичные координаты: [(x)/(длина век);(y)/(длина век)]
        else:
            direction = pygame.math.Vector2()

        return (distance, direction)
    def get_dialogue(self):
        hits = pygame.sprite.spritecollide(player_group, interaсtive_group, False)
        keys = pygame.key.get_pressed()
        intro = True
        if hits and keys[PLAYER_KEYS['usage_key']]:
            # screen.blit(self.dialogue_scr, (0,0))

            while intro:
                for event in pygame.event.get():  # тут мы получаем каждое отдельное событие из pygame
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER:
                        intro = False
            pygame.display.update()
    # def cooldowns(self):

    def get_damage(self, player):
        distance = self.get_player_distance_direction(player)[0]
        current_time = pygame.time.get_ticks()
        # print(player.attacking)
        if distance <= player.attack_radius and player.attacking:
            self.health -= weapon_data[player.weapon]['damage']
            print(self.health)
            self.hit_time = pygame.time.get_ticks()
        # else:

    def check_death(self):
        if self.health <= 0:
            self.kill()
    def animated(self):
        current_animation = self.animations[self.facing]
        # is_moving = self.direction.x != 0 or self.direction.y != 0

        if self.status == 'attack':
            self.facing = 'attack_' + self.facing if not 'attack' in self.facing else self.facing
        else:
            if 'attack' in self.facing:
                self.facing = self.facing.replace('attack_', '')
        self.frame_index += self.animation_speed if self.status != 'attack' else self.attack_animation_speed
        if self.frame_index >= len(current_animation):
            self.frame_index = 0

        self.image = current_animation[int(self.frame_index)]
    def update(self):
        # self.get_dialogue()
        self.movement(self.speed, 0.5)
        # print(f'max_trav_val: {self.max_traveling}, {self.rect}')
        self.animated()
        self.check_death()
class Tree(pygame.sprite.Sprite):
    def __init__(self, x, y, img, img_x, img_y, width, height):
        self._layer = PLAYER_LAYER
        self.sprite_type = 'tree'
        super().__init__(all_sprites, decorations_group)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = width
        self.height = height
        self.img_surface = img.get_sprite(img_x, img_y, self.width, self.height)

        self.image = pygame.transform.scale(self.img_surface, (self.img_surface.get_width() * 1.4, self.img_surface.get_height() * 1.4))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

class Walls(pygame.sprite.Sprite):
    def __init__(self, x, y, img, img_x, img_y, width, height):
        self.sprite_type = 'wall'
        super().__init__(all_sprites, walls_group)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = width
        self.height = height
        self.img_surface = img.get_sprite(img_x, img_y, self.width, self.height)

        self.image = pygame.transform.scale(self.img_surface, (self.img_surface.get_width() * 1.4, self.img_surface.get_height() * 1.4))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
class Ground(pygame.sprite.Sprite):
    def __init__(self, x, y, img, img_x, img_y, width, height):
        self._layer = GROUND_LAYER
        self.sprite_type = 'ground'
        super().__init__(all_sprites)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = width
        self.height = height
        self.img_surface = img.get_sprite(img_x, img_y, self.width, self.height)

        self.image = pygame.transform.scale(self.img_surface, (self.img_surface.get_width() * 1.4, self.img_surface.get_height() * 1.4))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

class InteractedObjs(pygame.sprite.Sprite):
    def __init__(self, x, y, img, img_x, img_y, width, height):
        self._layer = GROUND_LAYER
        self.sprite_type = 'object'
        super().__init__(all_sprites, decorations_group, interaсtive_group)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = width
        self.height = height
        self.weapon = list(weapon_data.keys())[0]
        self.direction = 'down'
        self.img_surface = img.get_sprite(img_x, img_y, self.width, self.height)

        self.y_change = 22
        self.is_looted = False

        # Message
        self.font = pygame.font.Font(r'E:\The Revenant\fonts\arial.ttf')
        self.msg_for_usage = self.font.render(f'Press: {PLAYER_KEYS["usage_key"]}', True, WHITE)
        self.msg_rect = self.msg_for_usage.get_rect()
        self.msg_rect.x = self.x
        self.msg_rect.y = self.y
        self.msg_surf = pygame.Surface((self.msg_rect.width, self.msg_rect.height))
        self.msg_isPrint = False

        # Анимации
        self.animations = {
            'down': [img.get_sprite(215, 264, self.width, self.height + 22),
                     img.get_sprite(118, 264, self.width, self.height + 22),
                     img.get_sprite(img_x, img_y, self.width, self.height)],

            'up': [img.get_sprite(img_x, img_y, self.width, self.height),
                   img.get_sprite(118, 264, self.width, self.height + 22),
                   img.get_sprite(215, 264, self.width, self.height + 22)]
        }
        self.animation_loop = 0
        self.index = 2

        self.image = pygame.transform.scale(self.img_surface, (self.img_surface.get_width() * 1.6, self.img_surface.get_height() * 1.4))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
    def collide_player(self):
        keys = pygame.key.get_pressed()
        hits = pygame.sprite.spritecollide(self, collisions_group, False)
        current_animation = self.animations[self.direction]

        if not hits and self.direction == 'up':
            self.index = 2
            self.rect.y += 22
            self.direction = 'down'
        if hits and self.direction != 'up':
            self.index = 1 if not self.is_looted else 2
            self.rect.y -= 22
            self.direction = 'up'
        if keys[PLAYER_KEYS['usage_key']] and self.direction == 'up' and self.is_looted is False:
            self.index = 2
            self.is_looted = True
        self.image = pygame.transform.scale(current_animation[self.index],
                                      (current_animation[self.index].get_width() * 1.6,
                                            current_animation[self.index].get_height() * 1.4))

        # if self.animation_loop >= len(current_animation):
        #     self.animation_loop = 0

    def info(self):
        pass
        # hits = pygame.sprite.spritecollide(collisions_group, interaсtive_group, False)
        # if hits:
        #     # Отображаем сообщение в прямоугольнике
        #     self.display_surface.blit(self.msg_for_usage, self.msg_rect)
        #     self.msg_isPrint = True
        # if not hits and self.msg_isPrint:
        #     self.display_surface.fill(BACKGROUND_COLOR, (hits[0].rect.x, hits[0].rect.y, hits[0].rect.width, hits[0].rect.height))
        #
        #     # Сбрасываем флаг
        #     self.msg_isPrint = False
    def update(self):
        self.info()
        self.collide_player()


class Timer:
    def __init__(self, duration, func = None):
        self.duration = duration
        self.func = func
        self.start_time = 0
        self.active = False
        # self.clock = pygame.time.Clock()
        # pygame.display.update()
    def activate(self):
        self.active = True
        self.start_time = pygame.time.get_ticks()
    def deactivate(self):
        if self.start_time == self.duration:

            self.active = False
            self.start_time = 0

    def upload(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration:
            self.deactivate()
            if self.func:
                self.func()

class Button:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()

        self.rect.x = self.x
        self.rect.y = self.y

    def is_pressed(self, pos, pressed):
        if self.rect.collidepoint(pos):
            if pressed[0]:
                return True
            return False