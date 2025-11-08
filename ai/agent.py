from typing import Tuple
from game.board import Board

class Agent:
    def choose_move(self, board: Board) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Choose a move (big_row, big_col, small_row, small_col) given the current board state."""
        raise NotImplementedError
