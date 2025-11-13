import time
from heapq import nlargest
from .agent import Agent
from game.board import Board
from utils.utils import Move

class MinimaxAgent(Agent):
    INF = 90129012

    def __init__(self, eval_fn:callable, time_limit:float=0.5):
        self.eval_fn = eval_fn
        self.time_limit = time_limit


    def choose_move(self, board: Board) -> Move:
        start_time = time.time()
        best_move = None
        depth = 1

        while True:
            if time.time() - start_time > self.time_limit:
                break
            try:
                # Run minimax at current depth
                top_lines = self.calculate_lines(board, depth, n=1)
                best_move = top_lines[0][1][0]  # take first move of top line
            except TimeoutError:
                break
            depth += 1  # increase depth for next iteration

        return best_move
    

    def calculate_lines(self, board:Board, max_depth:int, n:int=1) -> list[tuple[float, list[Move]]]:
        scored_moves = []
        alpha, beta = -self.INF, self.INF

        for move in board.legal_moves():
            board.make_move(move)
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
            board.make_move(move)
            score = -self._minimax(board, depth - 1, -beta, -alpha)
            board.undo_move()

            max_eval = max(max_eval, score)
            alpha = max(alpha, score)
            if alpha >= beta:
                break  # alpha-beta cutoff

        return max_eval
