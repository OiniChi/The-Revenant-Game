import pygame
# from settings import *
# directions = {
#     'pygame.K_a': ('x_change', -PLAYER_SPEED, 'left', 'attack_left'),
#     'pygame.K_d': ('x_change', PLAYER_SPEED, 'right', 'attack_right'),
#     'pygame.K_w': ('y_change', -PLAYER_SPEED, 'up', 'attack_up'),
#     'pygame.K_s': ('y_change', PLAYER_SPEED, 'down', 'attack_down'),
#     'pygame.K_SPACE': ('attack', 0, '', '')
# }
#
#
# def movement(directionss):
#     keys_list = list(directionss.keys())
#     index = 0
#
#     listic = [value[3] for key, value in directions.items()]
#     print(listic)
#
# movement(directions)
direction = pygame.math.Vector2()
for i in range(0, 5):
    direction.x -= 1
print(direction.x)

