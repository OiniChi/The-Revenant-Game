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

class Entity(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.frame_index = 0
        self.animation_speed = 0.15
        self.attack_animation_speed = 0.13
        self.direction = pygame.math.Vector2()
    def movement(self, entity_speed, multiplier):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
        self.rect.x += self.direction.x * entity_speed * multiplier
        self.collision_block('x', entity_speed, multiplier)
        self.rect.y += self.direction.y * entity_speed * multiplier
        self.collision_block('y', entity_speed, multiplier)

    def collision_block(self, direction, entity_speed, entity_score_coeff):
        keys = pygame.key.get_pressed()
        hits = pygame.sprite.spritecollide(self, walls_group, False)
        multiplier = entity_score_coeff ** 2 if keys[pygame.K_LSHIFT] else 1

        if direction == "x":
            if hits:
                if self.direction.x > 0:
                    self.rect.x = hits[0].rect.left - self.rect.width
                elif self.direction.x < 0:
                    self.rect.x = hits[0].rect.right
                for sprite in all_sprites:
                    sprite.rect.x += entity_speed * multiplier if self.direction.x > 0 else -entity_speed * multiplier

        elif direction == "y":
            if hits:
                if self.direction.y > 0:
                    self.rect.y = hits[0].rect.top - self.rect.height
                elif self.direction.y < 0:
                    self.rect.y = hits[0].rect.bottom
                for sprite in all_sprites:
                    sprite.rect.y += entity_speed * multiplier if self.direction.y > 0 else -entity_speed * multiplier
    # def get_heir_speed(self, heir):
    #     if heir == 'player':

