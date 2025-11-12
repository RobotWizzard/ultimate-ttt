import pygame
from game.board import Board
from .small_board_view import SmallBoardView

class BoardView:
    def __init__(self, board:Board, pos:tuple[int, int]=(0,0), size:int=600):
        self.board = board
        self.pos = pos
        self.size = size
        self.small_board_views = []
        self.offset = 20  # margin between small boards
        self.small_board_size = (size - 2 * self.offset) // 3
        for i in range(9):
            r, c = divmod(i, 3)
            sb_pos = (pos[0] + c * (self.small_board_size + self.offset), pos[1] + r * (self.small_board_size + self.offset))
            sb_view = SmallBoardView(board.boards[i], sb_pos, self.small_board_size,
                                     grid_pos=(r, c), global_board=board,
                                     is_active=(board.active_board is None or board.active_board == i))
            self.small_board_views.append(sb_view)

    def draw(self, screen):
        for sbv in self.small_board_views:
            sbv.draw(screen)
        
        # if the global board is won, draw the winning line
        if self.board.winner is not None:
            _, win_line = self.board.get_winner()
            start_big = win_line[0]
            end_big = win_line[2]
            # horizontal
            if start_big[0] == end_big[0]:
                start_x = self.pos[0] + (start_big[1]) * self.small_board_size
                start_y = self.pos[1] + (start_big[0] + 0.5) * self.small_board_size + (start_big[0] * self.offset)
                end_x = self.pos[0] + (end_big[1] + 1) * self.small_board_size + 2*self.offset
                end_y = self.pos[1] + (end_big[0] + 0.5) * self.small_board_size + (start_big[0] * self.offset)
            elif start_big[1] == end_big[1]:  # vertical
                start_x = self.pos[0] + (start_big[1] + 0.5) * self.small_board_size + (start_big[1] * self.offset)
                start_y = self.pos[1] + (start_big[0]) * self.small_board_size
                end_x = self.pos[0] + (end_big[1] + 0.5) * self.small_board_size + (start_big[1] * self.offset)
                end_y = self.pos[1] + (end_big[0] + 1) * self.small_board_size + 2*self.offset
            else:  # diagonal
                if start_big == (0, 0) and end_big == (2, 2):
                    start_x = self.pos[0]
                    start_y = self.pos[1]
                    end_x = self.pos[0] + self.size
                    end_y = self.pos[1] + self.size
                else:
                    start_x = self.pos[0] + self.size
                    start_y = self.pos[1]
                    end_x = self.pos[0]
                    end_y = self.pos[1] + self.size
            pygame.draw.line(screen, (0, 0, 0), (start_x, start_y), (end_x, end_y), width=5)

        # draw grid lines
        # for i in range(1, 3):
        #     pygame.draw.line(screen, (0, 0, 0),
        #                      (self.pos[0], self.pos[1] + i * (self.size // 3)),
        #                      (self.pos[0] + self.size, self.pos[1] + i * (self.size // 3)), width=3)
        #     pygame.draw.line(screen, (0, 0, 0),
        #                      (self.pos[0] + i * (self.size // 3), self.pos[1]),
        #                      (self.pos[0] + i * (self.size // 3), self.pos[1] + self.size), width=3)
    
    def update(self):
        for sbv in self.small_board_views:
            sbv.is_active = (self.board.active_board is None or
                             self.small_board_views.index(sbv) == self.board.active_board)
            sbv.update()
        if self.board.is_terminal():
            # if the global board is won, deactivate all small boards
            for sbv in self.small_board_views:
                sbv.is_active = False
    
    def handle_event(self, event):
        for sbv in self.small_board_views:
            sbv.handle_event(event)
