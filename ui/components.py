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


class Dropdown:
    def __init__(self, rect:pygame.typing.RectLike, options:list[str], font:pygame.font.Font,
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
    