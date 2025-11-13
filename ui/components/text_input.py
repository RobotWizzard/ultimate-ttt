import pygame
from ui.config import DEFAULT_FONT

class TextInput:
    def __init__(self, rect, text="", font=DEFAULT_FONT, text_color=(0, 0, 0), bg_color=(220, 220, 220), border_color=None,
                 on_submit=None):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.text_color = text_color
        self.bg_color = bg_color
        self.border_color = border_color
        self.text = text
        self.on_submit = on_submit

        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_interval = 500  # ms

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Click toggles focus
            is_active = self.rect.collidepoint(event.pos)
            if self.active and not is_active:
                self.on_submit(self.text)
            self.active = is_active
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                if self.on_submit is not None:
                    self.on_submit(self.text)
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.active = False
            else:
                # Add typed character
                self.text += event.unicode

    def update(self):
        if self.active:
            self.cursor_timer += pygame.time.get_ticks() % self.cursor_interval
            # Blink cursor
            if pygame.time.get_ticks() % (self.cursor_interval * 2) < self.cursor_interval:
                self.cursor_visible = True
            else:
                self.cursor_visible = False

    def draw(self, surface):
        # Background
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=5)
        if self.border_color is not None:
            pygame.draw.rect(surface, self.border_color, self.rect, width=2)

        # Render text
        margin = self.rect.width // 10
        text_surf = self.font.render(self.text, True, self.text_color)
        surface.blit(text_surf, (self.rect.x + margin, self.rect.y + self.rect.height - text_surf.get_height()))

        # Cursor
        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + margin + text_surf.get_width() + 1
            cursor_y = self.rect.y + (self.rect.height - text_surf.get_height()) // 2
            pygame.draw.line(surface, self.text_color, (cursor_x, cursor_y), (cursor_x, cursor_y + text_surf.get_height()))
