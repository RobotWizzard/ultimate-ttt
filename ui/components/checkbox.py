import pygame

class Checkbox:
    def __init__(self, x:int, y:int, size:int=32, border_color:pygame.typing.ColorLike=(100, 100, 100), border_width:int=4,
                 checked:bool=False, on_toggle:callable=None):
        self.rect:pygame.rect.Rect = pygame.Rect(x, y, size, size)
        self.size:int = size
        self.color:pygame.typing.ColorLike = border_color
        self.border_width:int = border_width
        self.checked:bool = checked
        self.on_toggle:callable = on_toggle

    def draw(self, surface:pygame.Surface):
        rect = pygame.draw.rect(surface, self.color, self.rect, width=self.border_width, border_radius=4)
        if self.checked:  # Draw a tick
            half_size = (self.size - 2 * self.border_width) // 2
            margin = (self.size - 2 * self.border_width) // 8
            pygame.draw.line(surface, (0, 0, 0),
                             (rect.x + self.border_width + margin, rect.y + self.border_width + half_size),
                             (rect.x + self.border_width + half_size - margin, rect.y + self.size - self.border_width - margin),
                             4)
            pygame.draw.line(surface, (0, 0, 0),
                             (rect.x + self.border_width + half_size - margin, rect.y + self.size - self.border_width - margin),
                             (rect.x + self.size - self.border_width - margin, rect.y + self.border_width + margin),
                             4)

    def handle_event(self, event:pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                if self.on_toggle:
                    self.on_toggle(self.checked)


class CheckboxWithLabel:
    def __init__(self, x:int, y:int, size:int,
                 text:str, font:pygame.font.Font, text_color:pygame.typing.ColorLike=(0, 0, 0),
                 border_color:pygame.typing.ColorLike=(100, 100, 100), border_width:int=4,
                 checked:bool=False, on_toggle:callable=None):
        self.rect:pygame.rect.Rect = pygame.Rect(x, y, size, size)
        self.text:str = text
        self.font:pygame.font.Font = font
        self.text_color:pygame.typing.ColorLike = text_color
        self.checked:bool = checked

        self.checkbox = Checkbox(self.rect.x, self.rect.y, size=size,
                                 border_color=border_color, border_width=border_width,
                                 checked=checked, on_toggle=on_toggle)

        text_x = self.rect.x + size + 10
        text_y = self.rect.y + (self.rect.height - font.get_height()) // 2
        self.text_pos = (text_x, text_y)
    
    def draw(self, surface:pygame.Surface):
        self.checkbox.draw(surface)
        text_surf = self.font.render(self.text, True, self.text_color)
        surface.blit(text_surf, self.text_pos)

    def handle_event(self, event:pygame.event.Event):
        self.checkbox.handle_event(event)
        self.checked = self.checkbox.checked
