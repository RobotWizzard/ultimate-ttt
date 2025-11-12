import pygame
from .scene import Scene
from .components import Button

class MenuScene(Scene):
    def __init__(self, screen, manager):
        self.screen = screen
        self.manager = manager

        self.start_button = Button(
            rect=(250, 250, 300, 60),
            text="Start Game",
            font=pygame.font.SysFont("Berlin Sans FB", 36),
            bg_color=(220, 220, 220),
            text_color=(0, 0, 0),
            hover_color=(200, 200, 200),
            on_click=self.start_game
        )

        self.analyse_game_button = Button(
            rect=(250, 320, 300, 60),
            text="Analyse Game",
            font=pygame.font.SysFont("Berlin Sans FB", 36),
            bg_color=(220, 220, 220),
            text_color=(0, 0, 0),
            hover_color=(200, 200, 200),
            on_click=None
        )
    
    def start_game(self):
        from .game_scene import GameScene
        game_scene = GameScene(self.screen, self.manager)
        self.manager.set_scene(game_scene)
    
    def update(self):
        self.start_button.update()
        self.analyse_game_button.update()

    def handle_event(self, event):
        self.start_button.handle_event(event)
        self.analyse_game_button.handle_event(event)

    def draw(self):
        self.screen.fill((250, 250, 250))
        title = pygame.font.SysFont("Harlow Solid", 72).render("Ultimate Tic-Tac-Toe", True, (0, 0, 0))
        self.screen.blit(title, (80, 100))
        self.start_button.draw(self.screen)
        self.analyse_game_button.draw(self.screen)
