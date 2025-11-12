import pygame
from game.smallboard import SmallBoard
from game.board import Board
from utils.cell import Cell
from .components import Button
from .config import HIGHLIGHT_COLOR, X_COLOR, O_COLOR, DEFAULT_FONT

class SmallBoardView:
    def __init__(self, board:SmallBoard, pos:tuple[int, int], size:int,
                 grid_pos:tuple[int, int], global_board:Board, is_active:bool = True):
        self.board = board
        self.pos = pos
        self.size = size
        self.cell_size = size // 3
        self.rect = pygame.Rect(pos[0], pos[1], size, size)
        self.is_active = is_active
        self.global_board = global_board
        self.grid_pos = grid_pos  # position of this small board in the global board
        self.buttons: list[Button | None] = [None] * 9  # pre-allocate

        # initialize buttons
        for idx in range(9):
            r, c = SmallBoard.index_to_coords(idx)
            rect = self.get_cell_rect(r, c)
            self.buttons[idx] = Button(rect, "", DEFAULT_FONT, bg_color=(255, 255, 255), hover_color=(200, 200, 200),
                                       on_click=lambda r=r, c=c:self.button_on_click(r, c))
    
    def button_on_click(self, r, c):
        idx = SmallBoard.coords_to_index(r, c)
        self.buttons[idx] = None
        if self.board.cells[idx] == Cell.EMPTY:
            self.global_board.make_move(self.grid_pos, (r, c))

    def draw(self, screen):
        # draw grid background
        pygame.draw.rect(screen, (255, 255, 255), self.rect)

        # draw cells
        for idx, cell in enumerate(self.board.cells):
            r, c = SmallBoard.index_to_coords(idx)
            if cell == Cell.EMPTY:
                if self.is_active:
                    self.buttons[idx].draw(screen)
            else:
                self.draw_mark(screen, r, c, cell)

        # draw grid lines
        for i in range(1, 3):
            pygame.draw.line(screen, (0, 0, 0),
                             (self.rect.left, self.rect.top + i * self.cell_size),
                             (self.rect.right, self.rect.top + i * self.cell_size))
            pygame.draw.line(screen, (0, 0, 0),
                             (self.rect.left + i * self.cell_size, self.rect.top),
                             (self.rect.left + i * self.cell_size, self.rect.bottom))
        
        # highlight if active
        margin = 4
        if self.is_active:
            highlight_rect = pygame.Rect(self.rect.left - margin, self.rect.top - margin,
                                         self.size + 2 * margin, self.size + 2 * margin)
            pygame.draw.rect(screen, HIGHLIGHT_COLOR, highlight_rect, width=2, border_radius=5)
        
        if self.board.winner is not None:
            # overlay a semi-transparent layer to indicate won board
            overlay = pygame.Surface((self.size + 2*margin, self.size + 2*margin), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (200, 200, 200, 120), overlay.get_rect(), border_radius=5)
            screen.blit(overlay, (self.rect.left - margin, self.rect.top - margin))
            # draw a big winner mark
            self.draw_winner_mark(screen, self.board.winner)

    def draw_winner_mark(self, screen, winner):
        center_x = self.rect.left + self.size // 2
        center_y = self.rect.top + self.size // 2
        if winner == Cell.X:
            pygame.draw.line(screen, X_COLOR, (center_x - 40, center_y - 40), (center_x + 40, center_y + 40), 8)
            pygame.draw.line(screen, X_COLOR, (center_x - 40, center_y + 40), (center_x + 40, center_y - 40), 8)
        else:
            pygame.draw.circle(screen, O_COLOR, (center_x, center_y), 50, 8)

    def draw_mark(self, screen, r, c, player):
        x = self.rect.left + c * self.cell_size + self.cell_size // 2
        y = self.rect.top + r * self.cell_size + self.cell_size // 2
        if player == Cell.X:
            pygame.draw.line(screen, X_COLOR, (x - 10, y - 10), (x + 10, y + 10), 3)
            pygame.draw.line(screen, X_COLOR, (x - 10, y + 10), (x + 10, y - 10), 3)
        else:
            pygame.draw.circle(screen, O_COLOR, (x, y), 10, 3)

    def get_cell_rect(self, row, col):
        return pygame.Rect(
            self.rect.left + col * self.cell_size,
            self.rect.top + row * self.cell_size,
            self.cell_size,
            self.cell_size
        )

    def update(self):
        for button in self.buttons:
            if button:
                button.update()

    def handle_event(self, event):
        if not self.is_active:
            return
        for button in self.buttons:
            if button:
                button.handle_event(event)
