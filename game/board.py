from typing import List, Optional, Tuple
from utils.cell import Cell, other
from game.smallboard import SmallBoard

class Board:
    # 0 1 2
    # 3 4 5
    # 6 7 8
    # position = (row, col), (0,0) is top-left
    WIN_COMBINATIONS = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
                        (0, 3, 6), (1, 4, 7), (2, 5, 8),
                        (0, 4, 8), (2, 4, 6)]
    def __init__(self):
        self.boards: List[SmallBoard] = [SmallBoard() for _ in range(9)]
        self.global_board: List[Cell] = [Cell.EMPTY] * 9
        self.active_board: Optional[int] = None  # 0..8 or None meaning "any"
        self.to_move: Cell = Cell.X
        self.winner: Optional[Cell] = None
    
    @staticmethod
    def index_to_coords(index: int) -> Tuple[int, int]:
        return (index // 3, index % 3)
    
    @staticmethod
    def coords_to_index(row: int, col: int) -> int:
        return row * 3 + col
    
    def _make_move(self, big_pos: int, small_pos: int):
        """Make a move given big and small board indices."""
        if self.active_board is not None and big_pos != self.active_board:
                raise ValueError("Must play in the active board")

        board = self.boards[big_pos]
        board._make_move(small_pos, self.to_move)

        if board.winner is not None:
            self.global_board[big_pos] = board.winner
        if self.boards[small_pos].winner is None and not self.boards[small_pos].is_full:
            self.active_board = small_pos
        else:
            self.active_board = None

        self.winner = self._check_winner()
        self.to_move = other(self.to_move)
    
    def make_move(self, big_pos: Tuple[int, int], small_pos: Tuple[int, int]):
        """Make a move given big and small board coordinates."""
        self._make_move(self.coords_to_index(big_pos[0], big_pos[1]),
                       self.coords_to_index(small_pos[0], small_pos[1]))
    
    def legal_moves(self) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Return a list of legal moves as ((big_row, big_col), (small_row, small_col))."""
        moves = []
        boards_to_consider = [self.active_board] if self.active_board is not None else range(9)
        for big_pos in boards_to_consider:
            board = self.boards[big_pos]
            if board.winner is None and not board.is_full:
                for small_pos in board.legal_moves():
                    moves.append((self.index_to_coords(big_pos), small_pos))
        return moves
    
    def is_terminal(self) -> bool:
        """Check if the game is over."""
        return self.winner is not None or all(board.is_full or board.winner is not None for board in self.boards)
    
    def _check_winner(self) -> Optional[Cell]:
        for combo in self.WIN_COMBINATIONS:
            if (self.global_board[combo[0]] != Cell.EMPTY and
                self.global_board[combo[0]] == self.global_board[combo[1]] == self.global_board[combo[2]]):
                return self.global_board[combo[0]]
        return None

    def copy(self) -> 'Board':
        """Create a deep copy of the board state."""
        new = Board()
        new.boards = [SmallBoard() for _ in range(9)]
        for i in range(9):
            new.boards[i].cells = self.boards[i].cells[:]
            new.boards[i].winner = self.boards[i].winner
            new.boards[i].is_full = self.boards[i].is_full
        new.global_board = self.global_board[:]
        new.active_board = self.active_board
        new.to_move = self.to_move
        new.winner = self.winner
        return new

    def __str__(self) -> str:
        rows = []
        for big_row in range(3):
            for small_row in range(3):
                row_cells = []
                for big_col in range(3):
                    board_index = big_row * 3 + big_col
                    board = self.boards[board_index]
                    for small_col in range(3):
                        cell_index = small_row * 3 + small_col
                        cell = board.cells[cell_index]
                        if cell == Cell.EMPTY:
                            row_cells.append('.')
                        elif cell == Cell.X:
                            row_cells.append('X')
                        else:
                            row_cells.append('O')
                    if big_col < 2:
                        row_cells.append('|')
                rows.append(' '.join(row_cells))
            if big_row < 2:
                rows.append('-' * 21)
        return '\n'.join(rows)
