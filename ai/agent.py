from game.board import Board
from utils.utils import Move

class Agent:
    def choose_move(self, board: Board) -> Move:
        """Choose a move given the current board state."""
        raise NotImplementedError
    
    def calculate_lines(self, board:Board, n:int=1) -> list[tuple[float, list[Move]]]:
        """Calculate the top n lines and return them as a list of (eval, [move, ...])."""
        raise NotImplementedError
