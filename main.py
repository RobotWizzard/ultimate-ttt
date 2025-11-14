def main():
    import pygame
    pygame.init()
    from ui.config import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE
    from ui.scenes import SceneManager, MenuScene
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    pygame.display.set_icon(pygame.image.load("ui/assets/icon.png").convert_alpha())
    clock = pygame.time.Clock()

    manager = SceneManager(screen)
    menu = MenuScene(screen, manager)

    manager.set_scene(menu)

    running = True
    while running:
        for event in pygame.event.get():
            manager.handle_event(event)
            if event.type == pygame.QUIT:
                running = False

        manager.update()
        manager.draw()
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
