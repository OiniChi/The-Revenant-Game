# Настройки игры
WIN_WIDTH = 1920  #(временно)
WIN_HEIGHT = 1080  #(временно)
TILESIZE = 42  # Размер плиты

CAMERA_ZOOM_SPEED = 0.17
FPS = 60

# Общеигровые цвета
WHITE = (255, 255, 255)
BLUE = (0, 154, 255)
BLACK = (0, 0, 0)
YELLOW = (249, 234, 25)

# Слои
PLAYER_LAYER = 3  # Приоритет отображения слоя игрока
ENEMY_LAYER = 3  # Приоритет отображения слоя врага
WALL_LAYER = 4  # Приоритет отображения слоя стены
GROUND_LAYER = 1  # Приоритет отображения слоя пола

# Player Data
PLAYER_SPEED = 7
PLAYER_SCORE_COEFF = 2
player_data = {
    'people': {'health': 100, 'damage': 20, 'attack_sound': '', 'speed': 11, 'attack_radius': 80, 'notice_radius': 360}
}

# Enemy Data
ENEMY_SPEED = 7
monster_data = {
    'zoombe': {'health': 100, 'damage': 20, 'attack_sound': '', 'speed': 4, 'attack_radius': 80, 'notice_radius': 360}
}


