import pygame
from ui.config import DEFAULT_FONT

class Dropdown:
    def __init__(self, rect:pygame.typing.RectLike, options:list[str], font:pygame.font.Font=DEFAULT_FONT,
                 bg_color:pygame.typing.ColorLike=(200, 200, 200),
                 options_color:pygame.typing.ColorLike=(220, 220, 220), 
                 text_color:pygame.typing.ColorLike=(0, 0, 0),
                 on_select:callable=None):
        self.rect:pygame.rect.Rect = pygame.Rect(rect)
        self.options:list[str] = options
        self.font:pygame.font.Font = font
        self.bg_color:pygame.typing.ColorLike = bg_color
        self.options_color:pygame.typing.ColorLike = options_color
        self.text_color:pygame.typing.ColorLike = text_color
        self.on_select:callable = on_select

        self.is_open:bool = False
        self.selected_index:int = 0
    
    def draw(self, surface:pygame.Surface):
        pygame.draw.rect(surface, self.bg_color, self.rect)
        selected_text_surf = self.font.render(self.options[self.selected_index], True, self.text_color)
        selected_text_rect = selected_text_surf.get_rect(center=self.rect.center)
        surface.blit(selected_text_surf, selected_text_rect)

        if self.is_open:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height,
                                          self.rect.width, self.rect.height)
                pygame.draw.rect(surface, self.options_color, option_rect)
                option_text_surf = self.font.render(option, True, self.text_color)
                option_text_rect = option_text_surf.get_rect(center=option_rect.center)
                surface.blit(option_text_surf, option_text_rect)
    
    def handle_event(self, event:pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_open = not self.is_open
            elif self.is_open:
                for i in range(len(self.options)):
                    option_rect = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height,
                                              self.rect.width, self.rect.height)
                    if option_rect.collidepoint(event.pos):
                        self.selected_index = i
                        self.is_open = False
                        if self.on_select:
                            self.on_select(self.options[i])
                        break
                else:
                    self.is_open = False
    
    def get_text(self):
        return self.options[self.selected_index]
