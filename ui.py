import pygame
from groups import enemy_group
from settings import *

class UI:
    def __init__(self):
        # general
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(r'fonts\arial.ttf', 64)

        # таймер
        self.secs = 0
        self.mins = 0
        self.font = pygame.font.Font(r'fonts\arial.ttf', 64)
        self.text = self.font.render("{}:{}".format(self.mins, self.secs), True, (255, 255, 255),
                                     (0, 0, 0))
        self.text.set_colorkey(BLACK)
        self.textRect = self.text.get_rect()
        self.textRect.center = WIN_WIDTH // 2, 60

        # bar setup
        self.health_bar_rect = pygame.Rect(10, 10, HEALTH_BAR_WIDTH, BAR_HEIGHT)

        self.ended_games = 0

    def show_bar(self, current, max_amount, bg_rect, color):
        # draw bg
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)

        # converting stat to pixel
        ratio = current / max_amount
        current_width = bg_rect.width * ratio
        current_rect = bg_rect.copy()
        current_rect.width = current_width

        # drawing the bar
        pygame.draw.rect(self.display_surface, color, current_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

    def clock_activate(self):
        self.display_surface.blit(self.text, self.textRect)
        self.secs += 1
        if self.secs == 60:
            self.secs = 0
            self.mins += 1

        self.text = self.font.render("{}:{}".format(self.mins, self.secs), True, (255, 255, 255),
                                     (0, 0, 0))
        self.text.set_colorkey(BLACK)
    def game_info(self):
        if len(enemy_group) == 0:
            self.ended_games += 1
        text1Rect = self.text.get_rect()
        text1Rect.center = 1690, 462
        text2 = self.font.render("{}".format(self.ended_games),True, (255, 255, 255),
                                     (0, 0, 0))
        text2.set_colorkey(BLACK)
        text2Rect = text2.get_rect()
        text2Rect.center = 230, 462
        self.display_surface.blit(self.text, text1Rect)
        self.display_surface.blit(text2, text2Rect)
    def display(self, player):
        self.show_bar(player.health, player_data['people']['health'], self.health_bar_rect, '#800000')
        if player.is_equipped:
            self.clock_activate()

