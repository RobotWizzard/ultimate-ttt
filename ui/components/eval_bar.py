import pygame
from ui.config import DEFAULT_FONT

class EvalBar:
    def __init__(self, x, y, width, height, font=DEFAULT_FONT):
        self.rect = pygame.Rect(x, y, width, height)
        self.value = 0.0  # engine eval, positive = X better
        self.max_eval = 5.0  # max range shown
        self.line1 = (0.0, [])  # (eval, [moves])
        self.line2 = (0.0, [])
        self.font = font
        self.small_font = pygame.font.SysFont("Berlin Sans FB", 18)
        self.bg_color = (30, 30, 30)
        self.white_color = (240, 240, 240)
        self.black_color = (20, 20, 20)
        self.border_color = (80, 80, 80)
        self.bar_color = (100, 220, 100)

        # for smooth animation
        self.display_value = 0.0

    def set_value(self, value: float):
        self.value = max(-self.max_eval, min(self.max_eval, value))

    def set_line1(self, line:tuple[float, list[str]]):
        self.line1 = line
    def set_line2(self, line:tuple[float, list[str]]):
        self.line2 = line

    def set_lines(self, lines:tuple[tuple[float, list[str]], tuple[float, list[str]]]):
        self.set_line1(lines[0])
        self.set_line2(lines[1])

    def draw(self, screen):
        # background
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, width=2)

        # smooth interpolation
        self.display_value += (self.value - self.display_value) * 0.2

        # normalize eval: -max → 0, +max → 1
        normalized = (self.display_value + self.max_eval) / (2 * self.max_eval)
        normalized = max(0, min(1, normalized))

        # compute filled width
        fill_width = int(self.rect.width * normalized)
        fill_rect = pygame.Rect(self.rect.left, self.rect.top, fill_width, self.rect.height)

        # draw filled portion (white advantage)
        pygame.draw.rect(screen, (230, 230, 230), fill_rect)

        # draw eval text
        eval_rect_x = self.rect.centerx - self.rect.width // 16
        eval_rect_y = self.rect.centery - 10
        eval_rect = pygame.Rect(eval_rect_x, eval_rect_y, self.rect.width // 8, self.rect.height - 10)
        pygame.draw.rect(screen, (240, 240, 240), eval_rect, border_radius=4)
        eval_text = self.small_font.render(str(self.value), True, (0, 0, 0))
        text_pos = (self.rect.centerx - eval_text.get_width() // 2,
                    self.rect.centery - eval_text.get_height() // 2)
        screen.blit(eval_text, text_pos)

        # draw an "X" at the right end and "O" at the left end
        x_text = self.font.render("X", True, (200, 50, 50))
        o_text = self.font.render("O", True, (100, 100, 240))
        screen.blit(o_text, (self.rect.right - o_text.get_width() - 5, self.rect.centery - o_text.get_height() // 2))
        screen.blit(x_text, (self.rect.left + 5, self.rect.centery - x_text.get_height() // 2))

        # draw engine lines below
        # first line
        line_moves = ""
        for s in self.line1[1]:
            line_moves += " " + s
        y_offset = self.rect.bottom + 10
        color = (160, 160, 160)
        line_surface = self.small_font.render(f"{self.line1[0]} {line_moves}", True, color)
        screen.blit(line_surface, (self.rect.left, y_offset))

        # second line
        y_offset += 20
        line_moves = ""
        for s in self.line2[1]:
            line_moves += " " + s
        line_surface = self.small_font.render(f"{self.line2[0]} {line_moves}", True, color)
        screen.blit(line_surface, (self.rect.left, y_offset))
