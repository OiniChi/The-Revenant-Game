import time
import pygame
from config import *
from settings import *
from levels import *
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

        self.enemy_is_spawned = False
        # Загрузка спрайтов
        self.terrarian_spritesheet = Spritesheet('img/Level_textures/all_sprites.png')
        self.tree_spritesheet = Spritesheet('img/Level_textures/all_sprites.png')
        self.player_spritesheet = Spritesheet('img/Player/Movement/character.png')
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
        self.camera_offsetX = 0
        self.camera_offsetY = 0

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
                    self.player = Player(j, i, self.player_spritesheet, 41, 91)

        # Смещаем камеру(или все спрайты в игре) в цент игрока
        for sprite in all_sprites:  # !!!!!!!!!! ТУТ СМЕЩЕНИЕ КАМЕРА РАБОТАЕТ ТОЛЬКО ВНУТРИ ДИСПЛЕЯ, ЕСТЬ ПРОБЛЕМА СО СПАВНОМ ЗА ЕГО ПРЕДЕЛАМИ(доработать!)
            sprite.rect.x -= WIN_WIDTH - self.player.x + self.player.width if self.player.x > WIN_WIDTH / 2 else -(WIN_WIDTH + self.player.x - self.player.width)
            sprite.rect.y -= WIN_HEIGHT + self.player.y - self.player.height if self.player.y > WIN_WIDTH / 2 else -(WIN_HEIGHT - self.player.y + self.player.height)

        # Запоминаем на какую величину мы сдвинули камеру для корректного спавна Врагов
        self.camera_offsetX -= WIN_WIDTH - self.player.x + self.player.width
        self.camera_offsetY -= WIN_HEIGHT - self.player.y + self.player.height
    def spawn_enemies(self):
        hits = pygame.sprite.spritecollide(self.player, interaсtive_group, False)
        if hits and not self.enemy_is_spawned:
            for i, row in enumerate(objmap):
                for j, column in enumerate(row):
                    if column == "E":
                        Enemy(j, i, self.camera_offsetX + self.player.camX_change, self.camera_offsetY - self.player.camY_change, self.enemy_spritesheet, 42, 91)
                    if i == len(objmap) - 1 and j == len(row) - 1:
                        self.enemy_is_spawned = True
    def custom_draw(self):
        # Перерисовка декоративных объектов для разноплановости
        self.internal_surface.fill('#71ddee')

        for sprite in all_sprites:
            self.internal_surface.blit(sprite.image, sprite.rect)

        [2, 4, 5,12, 13]
        for sprite in sorted(decorations_group, key = lambda sprite: sprite.rect.centery):
            self.internal_surface.blit(sprite.image, sprite.rect)

        scaled_surf = pygame.transform.scale(self.internal_surface, self.internal_surface_size_vector * self.zoom_scale)
        scaled_rect = scaled_surf.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT / 2))

        all_sprites.update()
        self.display_surface.blit(scaled_surf, scaled_rect)
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, img, width, height):
        self._layer = PLAYER_LAYER
        super().__init__(all_sprites, decorations_group, collisions_group)

        self.animation_loop = 0
        self.attack_animation_loop = 0
        self.facing = 'down'

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = width
        self.height = height

        self.camX_change = 0
        self.camY_change = 0
        self.x_change = 0
        self.y_change = 0

        self.timers = {
            ''
        }

        self.is_equipped = False
        self.animations = {
            'down': [img.get_sprite(19, 21, self.width, self.height),
                     img.get_sprite(69, 21, self.width, self.height),
                     img.get_sprite(115, 21, self.width, self.height),
                     img.get_sprite(165, 21, self.width, self.height)],

            'up': [img.get_sprite(18, 127, 43, self.height),
                   img.get_sprite(67, 127, 39, self.height),
                   img.get_sprite(114, 127, 43, self.height),
                   img.get_sprite(165, 127, 39, self.height)],

            'left': [img.get_sprite(20, 352, 40, self.height),
                     img.get_sprite(68, 352, 40, self.height),
                     img.get_sprite(116, 352, 40, self.height),
                     img.get_sprite(164, 352, 40, self.height)],

            'right': [img.get_sprite(20, 239, self.width, self.height),
                      img.get_sprite(71, 239, 37, self.height),
                      img.get_sprite(116, 239, self.width, self.height),
                      img.get_sprite(163, 239, 40, self.height)],

            'attack_down': [img.get_sprite(16, 454, 49, 91),
                            img.get_sprite(69, 454, 39, 91),
                            img.get_sprite(113, 454, 49, 91)],

            'attack_up': [img.get_sprite(17, 550, 47, 91),
                          img.get_sprite(67, 550, 44, 91),
                          img.get_sprite(113, 550, 47, 91)],

            'attack_left': [img.get_sprite(21, 742, 40, 91), #20, 352
                            img.get_sprite(71, 742, 30, 91),
                            img.get_sprite(116, 742, 41, 91)],

            'attack_right': [img.get_sprite(20, 646, 41, 91),
                             img.get_sprite(66, 646, 51, 91),
                             img.get_sprite(117, 646, 41, 91)]
        }
        self.animation_index = 0
        self.directions = {
            pygame.K_a: ('x_change', -PLAYER_SPEED, 'left', 'attack_left'),
            pygame.K_d: ('x_change', PLAYER_SPEED, 'right', 'attack_right'),
            pygame.K_w: ('y_change', -PLAYER_SPEED, 'up', 'attack_up'),
            pygame.K_s: ('y_change', PLAYER_SPEED, 'down', 'attack_down'),
            # pygame.K_SPACE: ('attack', 0, '', '')
        }
        self.attack_keys = [value[3] for key, value in self.directions.items()]
        self.directions_keys = [value[2] for key, value in self.directions.items()]

        self.image = self.animations['down'][0]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
    def movement(self):
        keys = pygame.key.get_pressed()

        for i, (key, (change_attr, speed, facing, attack_facing)) in enumerate(self.directions.items()):
            if keys[key]:
                setattr(self, change_attr, speed if not keys[PLAYER_KEYS['speed_boost']] else speed * PLAYER_SCORE_COEFF)
                self.animation_index = i
                self.facing = facing

        if keys[pygame.K_SPACE] and self.is_equipped:
            pygame.sprite.spritecollide(self, enemy_group, True)
            self.facing = self.attack_keys[self.animation_index]
            for event in pygame.event.get():
                if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                    self.facing = self.directions_keys[self.animation_index]

            for key, (change_attr, speed, facing, attack_facing) in self.directions.items():
                if keys[key]:
                    setattr(self, change_attr, speed if not keys[PLAYER_KEYS['speed_boost']] else speed * PLAYER_SCORE_COEFF)
                    self.facing = 'attack_' + facing

        if keys[PLAYER_KEYS['up']] or keys[PLAYER_KEYS['down']]:
            for sprite in all_sprites:
                sprite.rect.y -= self.y_change if not keys[PLAYER_KEYS['speed_boost']] else self.y_change * PLAYER_SCORE_COEFF
            self.camY_change -= self.y_change if not keys[PLAYER_KEYS['speed_boost']] else self.y_change * PLAYER_SCORE_COEFF
        if keys[PLAYER_KEYS['left']] or keys[PLAYER_KEYS['right']]:
            for sprite in all_sprites:
                sprite.rect.x -= self.x_change if not keys[PLAYER_KEYS['speed_boost']] else self.x_change * PLAYER_SCORE_COEFF
            self.camX_change -= self.x_change if not keys[PLAYER_KEYS['speed_boost']] else self.x_change * PLAYER_SCORE_COEFF
    def animated(self):
        keys = pygame.key.get_pressed()
        direction = self.facing
        current_animation = self.animations[direction]
        is_moving = self.x_change != 0 or self.y_change != 0
        frame_index = 0
        index = math.floor(self.animation_loop)
        index2 = math.floor(self.attack_animation_loop)

        if not is_moving:
            if keys[PLAYER_KEYS['attack_key']] and self.is_equipped:
                frame_index = index2
                self.attack_animation_loop += 0.1
        else:
            frame_index = index - 1
            self.animation_loop += 0.1

        if self.animation_loop >= len(current_animation) or self.attack_animation_loop >= len(current_animation):
            self.animation_loop = 0
            self.attack_animation_loop = 0

        self.image = pygame.transform.scale(current_animation[frame_index],
                                            (current_animation[frame_index].get_width() * 1.4,
                                             current_animation[frame_index].get_height() * 1.4))

    def collide_enemy(self):
        # hits = pygame.sprite.spritecollide(self, enemy_group, False)
        #
        # if hits:
        #     self.kill()
        pass
    def collide_block(self, direction):
        keys = pygame.key.get_pressed()
        hits = pygame.sprite.spritecollide(self, walls_group, False)
        multiplier = PLAYER_SCORE_COEFF**2 if keys[pygame.K_LSHIFT] else 1

        if direction == "x":
            if hits:
                if self.x_change > 0:
                    self.rect.x = hits[0].rect.left - self.rect.width
                elif self.x_change < 0:
                    self.rect.x = hits[0].rect.right
                for sprite in all_sprites:
                    sprite.rect.x += PLAYER_SPEED * multiplier if self.x_change > 0 else -PLAYER_SPEED * multiplier

        elif direction == "y":
            if hits:
                if self.y_change > 0:
                    self.rect.y = hits[0].rect.top - self.rect.height
                elif self.y_change < 0:
                    self.rect.y = hits[0].rect.bottom
                for sprite in all_sprites:
                    sprite.rect.y += PLAYER_SPEED * multiplier if self.y_change > 0 else -PLAYER_SPEED * multiplier

    def collide_usebleObj(self):
        hits = pygame.sprite.spritecollide(self, interaсtive_group, False)
        keys = pygame.key.get_pressed()

        if hits and keys[PLAYER_KEYS['usage_key']]:
            self.is_equipped = True


    # Предназначен для обновления состояния игрока на каждом шаге игрового цикла
    def update(self):  # тут будет прописана логика обновления
        keys = pygame.key.get_pressed()
        multiplier = 1.5 if keys[PLAYER_KEYS['speed_boost']] else 1

        self.movement()
        self.animated()
        self.collide_usebleObj()
        self.collide_enemy()
        self.rect.x += self.x_change * multiplier
        self.collide_block('x')
        self.rect.y += self.y_change * multiplier
        self.collide_block('y')

        self.x_change = 0
        self.y_change = 0

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, i_x, i_y, img, width, height):
        self._layer = PLAYER_LAYER
        super().__init__(all_sprites, enemy_group, decorations_group)
        # Ширина 108 пикс
        # Длинна 305 пикс
        self.dialogue_scr = pygame.image.load('img/Menu/Dilogs/zombe_dialogue.png').convert()
        self.img = img
        self.x = x * TILESIZE + i_x
        self.y = y * TILESIZE - i_y
        self.width = width  # Ширина плиты
        self.height = height  # Длинна плиты

        self.x_change = 0
        self.y_change = 0

        #self.health = 100
        self.facing = random.choice(['left', 'right'])  # Сторона направления взгляда врага (по умолчанию: 'вниз')
        self.attack_animation_loop = 0
        self.animation_loop = 0
        self.movement_loop = 0
        self.max_traveling = random.randint(7, 30)

        # self.image = self.game.enemy_spritesheet.get_sprite(0, 0, 42, 90)  # Изображение врага
        self.image = self.img.get_sprite(0, 0, 40, 91)

        self.rect = self.image.get_rect()  # Хитбокс(габариты точки(x,y)) - (Размер спрайта врага = размеру прямоуг.)
        self.rect.x = self.x  # Положение хитбокса = положению  точки врага (по X и Y)
        self.rect.y = self.y

        self.animations = {
            'up': [img.get_sprite(1, 101, self.width, self.height),
                   img.get_sprite(50, 101, self.width, self.height),
                   img.get_sprite(97, 101, self.width, self.height),
                   img.get_sprite(148, 101, self.width, self.height)],

            'down': [img.get_sprite(2, 13, self.width, self.height),
                     img.get_sprite(52, 13, self.width, self.height),
                     img.get_sprite(98, 13, self.width, self.height),
                     img.get_sprite(147, 13, self.width, self.height)],

            'left': [img.get_sprite(0, 293, self.width, self.height),
                     img.get_sprite(48, 293, self.width, self.height),
                     img.get_sprite(96, 293, self.width, self.height),
                     img.get_sprite(148, 293, self.width, self.height)],

            'right': [img.get_sprite(1, 200, self.width, self.height),
                      img.get_sprite(49, 200, self.width, self.height),
                      img.get_sprite(97, 200, self.width, self.height),
                      img.get_sprite(145, 200, self.width, self.height)],

            'attack_up': [img.get_sprite(0, 677, self.width, self.height),
                            img.get_sprite(48, 677, self.width, self.height),
                            img.get_sprite(96, 677, self.width, self.height)],

            'attack_down': [img.get_sprite(0, 677, self.width, self.height),
                            img.get_sprite(48, 677, self.width, self.height),
                            img.get_sprite(96, 677, self.width, self.height)],
            'attack_left': [img.get_sprite(0, 677, self.width, self.height),
                            img.get_sprite(48, 677, self.width, self.height),
                            img.get_sprite(96, 677, self.width, self.height)],

            'attack_right': [img.get_sprite(6, 581, self.width, self.height),
                             img.get_sprite(54, 581, self.width, self.height),
                             img.get_sprite(102, 581, self.width, self.height)]
        }
        self.directions = {
            'l_key': ('x_change', -ENEMY_SPEED, 'left', 'attack_left'),
            'r_key': ('x_change', ENEMY_SPEED, 'right', 'attack_right'),
            'up_key': ('y_change', -ENEMY_SPEED, 'up', 'attack_up'),
            'down_key': ('y_change', ENEMY_SPEED, 'down', 'attack_down'),
        }
        self.attack_keys = [value[3] for key, value in self.directions.items()]
        self.directions_keys = [value[2] for key, value in self.directions.items()]
    def update(self):
        # self.get_dialogue()
        self.movement()
        self.animated()
        self.rect.x += self.x_change
        self.rect.y += self.y_change

        self.x_change = 0
        self.y_change = 0

        # Метод движения врага

    def movement(self):
        hits = pygame.sprite.spritecollide(self, collisions_group, False)
        random_key = random.choice(['left', 'right'])
        for i, (key, (change_attr, speed, facing, attack_facing)) in enumerate(self.directions.items()):
            if not hits:
                if key == 'l_key' or key == 'r_key':
                    setattr(self, change_attr, speed)
                    self.movement_loop -= 1 if key == 'l_key' else 1
                    # self.x_change -= ENEMY_SPEED if key == 'l_key' else ENEMY_SPEED
                    if self.movement_loop < self.max_traveling or self.movement_loop > -self.max_traveling:
                        self.movement_loop = 1 if key == 'l_key' else -1
                        self.facing = 'left' if key == 'l_key' else 'right'
                        # print(self.facing)
            # else:

        # if not hits:
        #     if self.facing == 'left':
        #         self.x_change -= ENEMY_SPEED
        #         self.movement_loop -= 1
        #         if self.movement_loop <= -self.max_traveling:
        #             self.facing = 'right'
        #     if self.facing == 'right':
        #         self.x_change += ENEMY_SPEED
        #         self.movement_loop += 1
        #         if self.movement_loop >= self.max_traveling:
        #             self.facing = 'left'
        # else:
        #     if self.facing == 'left':
        #         self.facing = 'attack_left'
        #         self.x_change -= ENEMY_SPEED
        #         self.movement_loop -= 1
        #         if self.movement_loop <= -self.max_traveling:
        #             self.facing = 'right'
        #     if self.facing == 'right':
        #         self.facing = 'attack_right'
        #         self.x_change += ENEMY_SPEED
        #         self.movement_loop += 1
        #         if self.movement_loop >= self.max_traveling:
        #             self.facing = 'left'
    # def get_dialogue(self):
    #     hits = pygame.sprite.spritecollide(player_group, interaсtive_group, False)
    #     keys = pygame.key.get_pressed()
    #     intro = True
    #     if hits and keys[PLAYER_KEYS['usage_key']]:
    #         screen.blit(self.dialogue_scr, (0,0))
    #
    #         while intro:
    #             for event in pygame.event.get():  # тут мы получаем каждое отдельное событие из pygame
    #                 if event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER:
    #                     intro = False
    #         pygame.display.update()
    def animated(self):
        hits = pygame.sprite.spritecollide(self, collisions_group, False)
        direction = self.facing
        current_animation = self.animations[direction]
        index = math.floor(self.animation_loop)
        index2 = math.floor(self.attack_animation_loop)
        is_moving = self.x_change != 0 or self.y_change != 0

        if not is_moving:
            if not hits:
                frame_index = 0
                self.facing = 'left' if direction == 'attack_left' and not hits else 'right' if direction == 'attack_right' and not hits else self.facing
            else:
                frame_index = index2
                self.attack_animation_loop += 0.1
                if self.attack_animation_loop >= len(current_animation):
                    self.attack_animation_loop = 0
        else:
            if not hits:
                frame_index = index
                self.animation_loop += 0.1
                if self.animation_loop >= len(current_animation):
                    self.animation_loop = 0
            else:
                frame_index = index2
                self.attack_animation_loop += 0.1
                if self.attack_animation_loop >= len(current_animation):
                    self.attack_animation_loop = 0

        self.image = pygame.transform.scale(current_animation[frame_index],
                                            (current_animation[frame_index].get_width() * 1.4,
                                             current_animation[frame_index].get_height() * 1.4))
class Tree(pygame.sprite.Sprite):
    def __init__(self, x, y, img, img_x, img_y, width, height):
        self._layer = PLAYER_LAYER
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
        super().__init__(all_sprites, decorations_group, interaсtive_group)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = width
        self.height = height

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