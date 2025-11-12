import pygame

class Button:
    def __init__(self, rect:pygame.typing.RectLike, text:str, font:pygame.font.Font,
                 bg_color:pygame.typing.ColorLike=(100, 100, 100), text_color:pygame.typing.ColorLike=(255, 255, 255),
                 hover_color:pygame.typing.ColorLike=(50, 50, 50),
                 on_click:callable=None):
        self.rect:pygame.rect.Rect = pygame.Rect(rect)
        self.text:str = text
        self.font:pygame.font.Font = font
        self.bg_color:pygame.typing.ColorLike = bg_color
        self.text_color:pygame.typing.ColorLike = text_color
        self.hover_color:pygame.typing.ColorLike = hover_color
        self.on_click:callable = on_click
        self.hovered = False

    def draw(self, surface:pygame.Surface):
        if self.hovered:
            pygame.draw.rect(surface, self.hover_color, self.rect)
        else:
            pygame.draw.rect(surface, self.bg_color, self.rect)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event:pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.on_click:
                self.on_click()