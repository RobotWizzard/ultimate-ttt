from heapq import nlargest
from .agent import Agent
from game.board import Board

class MinimaxAgent(Agent):
    INF = 90129012

    def __init__(self, eval_fn:callable, time_limit:float=1.0):
        self.eval_fn = eval_fn
        self.time_limit = time_limit


    def choose_move(self, board:Board) -> tuple[tuple[int, int], tuple[int, int]]:
        return self.calculate_lines(board, 5, n=1)[0][1][0]
    

    def calculate_lines(self, board:Board, max_depth:int, n:int=1) -> list[tuple[float, list[tuple[tuple[int, int], tuple[int, int]]]]]:
        scored_moves = []
        alpha, beta = -self.INF, self.INF

        for move in board.legal_moves():
            board.make_move(*move)
            score = -self._minimax(board, max_depth - 1, -beta, -alpha)
            board.undo_move()
            scored_moves.append((score, [move]))
            alpha = max(alpha, score)

        # Sort and keep top_k
        top_lines = nlargest(n, scored_moves, key=lambda x: x[0])

        return top_lines  # [(score, [move1, move2, ...]), ...]
    

    def _minimax(self, board:Board, depth:int, alpha:float, beta:float) -> float:
        if depth == 0 or board.is_terminal():
            return self.eval_fn(board)

        max_eval = -self.INF
        for move in board.legal_moves():
            board.make_move(*move)
            score = -self._minimax(board, depth - 1, -beta, -alpha)
            board.undo_move()

            max_eval = max(max_eval, score)
            alpha = max(alpha, score)
            if alpha >= beta:
                break  # alpha-beta cutoff

        return max_eval
