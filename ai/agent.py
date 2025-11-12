from game.board import Board

class Agent:
    def choose_move(self, board: Board) -> tuple[tuple[int, int], tuple[int, int]]:
        """Choose a move ((big_row, big_col), (small_row, small_col)) given the current board state."""
        raise NotImplementedError
    
    def calculate_lines(self, board:Board, n:int=1) -> list[tuple[float, list[tuple[tuple[int, int], tuple[int, int]]]]]:
        """Calculate the top n lines and return them as a list of (eval, [((big_row, big_col), (small_row, small_col)), ...])."""
        raise NotImplementedError
