import pygame
from ui.scene_manager import SceneManager
from ui.menu_scene import MenuScene

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Ultimate Tic-Tac-Toe")
    pygame.display.set_icon(pygame.image.load("ui/assets/icon.png").convert_alpha())
    clock = pygame.time.Clock()

    manager = SceneManager(screen)
    menu = MenuScene(screen, manager)

    manager.set_scene(menu)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            manager.handle_event(event)

        manager.update()
        manager.draw()
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
