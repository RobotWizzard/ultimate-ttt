import pygame

class Scene:
    def __init__(self, screen:pygame.Surface):
        self.screen:pygame.Surface = screen
    
    def draw(self):
        pass
    
    def handle_event(self, event:pygame.event.Event):
        pass
    
    def update(self):
        pass
    