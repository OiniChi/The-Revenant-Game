from config import *
from settings import *
from sprites import CameraGroup, Button
from groups import all_sprites, decorations_group, enemy_group
import sys

# Инициализируем основные поля для создания окнаd
pygame.init()
info = pygame.display.Info()
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('The Revenant')
clock = pygame.time.Clock()
cam_group = CameraGroup()
main_menu_spritesheet = pygame.image.load("img/Menu/MainScr.jpg").convert()

def intro_screen():
    intro = True
    screen.blit(main_menu_spritesheet, (0, 0))
    play_button = Button(765, 517, 360, 112)
    exit_button = Button(883, 709, 225, 63)


    while intro:
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        pygame.event.get()  # тут мы получаем каждое отдельное событие из pygame
        if exit_button.is_pressed(mouse_pos, mouse_pressed):
            pygame.quit()
            sys.exit()

        if play_button.is_pressed(mouse_pos, mouse_pressed):
            intro = False

        pygame.display.update()

def game_over():
    intro = True
    global spawn_flag
    screen.blit(main_menu_spritesheet, (0, 0))
    cam_group.gamePaused_info()
    play_button = Button(765, 517, 360, 112)
    exit_button = Button(883, 709, 225, 63)

    while intro:
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        for event in pygame.event.get():  # тут мы получаем каждое отдельное событие из pygame
            if exit_button.is_pressed(mouse_pos, mouse_pressed):
                pygame.quit()
                sys.exit()
            if play_button.is_pressed(mouse_pos, mouse_pressed):
                decorations_group.empty()
                spawn_flag = False
                all_sprites.empty()  # Очищаем группу спрайтов
                cam_group.__init__()
                all_sprites.update()
                intro = False  # Выходим из цикла
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                intro = False

        pygame.display.update()

if __name__ == "__main__":
    intro_screen()
    # Основной игровой цикл
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game_over()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_x:
                cam_group.spawn_enemies()
            elif event.type == pygame.MOUSEWHEEL:
                # Изменения масштаба камеры на скорость : 0,17
                cam_group.zoom_scale += CAMERA_ZOOM_SPEED if event.y > 0 else -CAMERA_ZOOM_SPEED

                # Ограничиваем масштаб в пределах
                cam_group.zoom_scale = max(0.84, min(1.45, cam_group.zoom_scale))

        screen.fill('#71ddee')
        cam_group.run()
        if cam_group.player.is_dead or len(enemy_group) == 0 and cam_group.player.is_equipped:
            game_over()
        pygame.display.update()
        clock.tick(60)