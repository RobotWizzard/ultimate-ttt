import pygame

class WinLossBar:
    def __init__(self, x, y, width, height, font=None, speed=0.5):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font or pygame.font.SysFont("Arial", 20)
        self.speed = speed  # interpolation speed (0-1)

        self.win_count = 0
        self.draw_count = 0
        self.loss_count = 0

        # current animated widths
        self.win_width = 0
        self.draw_width = 0
        self.loss_width = 0

        # colors
        self.win_color = (0, 200, 0)
        self.draw_color = (180, 180, 180)
        self.loss_color = (200, 0, 0)

    def set_results(self, wins, draws, losses):
        self.win_count = wins
        self.draw_count = draws
        self.loss_count = losses

    def update(self):
        total = self.win_count + self.draw_count + self.loss_count
        if total == 0:
            total = 1

        target_win = self.rect.width * (self.win_count / total)
        target_draw = self.rect.width * (self.draw_count / total)
        target_loss = self.rect.width * (self.loss_count / total)

        # simple linear interpolation
        self.win_width += (target_win - self.win_width) * self.speed
        self.draw_width += (target_draw - self.draw_width) * self.speed
        self.loss_width += (target_loss - self.loss_width) * self.speed

    def draw(self, surface):
        x = self.rect.x
        bar_y = self.rect.y + self.rect.height // 3
        total = self.win_count + self.draw_count + self.loss_count or 1
        win_pct = int(100 * self.win_count / total)
        draw_pct = int(100 * self.draw_count / total)
        loss_pct = int(100 * self.loss_count / total)

        # draw win segment
        win_count_label = self.font.render(str(self.win_count), True, self.win_color)
        surface.blit(win_count_label, win_count_label.get_rect(left=x, top=self.rect.y))
        win_seg = pygame.draw.rect(surface, self.win_color, (x, bar_y, int(self.win_width), self.rect.height//3),
                                   border_top_left_radius=5, border_bottom_left_radius=5)
        win_pct_label = self.font.render(f"{win_pct}% Won", True, self.win_color)
        surface.blit(win_pct_label, win_pct_label.get_rect(left=x, top=win_seg.bottom+5))
        x += int(self.win_width)

        # draw loss segment
        loss_count_label = self.font.render(str(self.loss_count), True, self.loss_color)
        surface.blit(loss_count_label, loss_count_label.get_rect(left=x, top=self.rect.y))
        loss_seg = pygame.draw.rect(surface, self.loss_color, (x, bar_y, int(self.loss_width), self.rect.height//3))
        loss_pct_label = self.font.render(f"{loss_pct}% Loss", True, self.loss_color)
        surface.blit(loss_pct_label, loss_pct_label.get_rect(left=x, top=loss_seg.bottom+5))
        x += int(self.loss_width)

        # draw draw segment
        draw_count_label = self.font.render(str(self.draw_count), True, self.draw_color)
        surface.blit(draw_count_label, draw_count_label.get_rect(left=x, top=self.rect.y))
        draw_seg = pygame.draw.rect(surface, self.draw_color, (x, bar_y, self.rect.right-x, self.rect.height//3),
                                   border_top_right_radius=5, border_bottom_right_radius=5)
        draw_pct_label = self.font.render(f"{draw_pct}% Draw", True, self.draw_color)
        surface.blit(draw_pct_label, draw_pct_label.get_rect(left=x, top=draw_seg.bottom+5))
