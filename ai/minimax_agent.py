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
    

    def calculate_lines(self, board: Board, max_depth: int, n: int = 1):
        """
        Returns top N lines from the current board.
        Each line is (score, [Move, Move, ...])
        """
        scored_lines = []
        alpha, beta = -self.INF, self.INF

        for move in board.legal_moves():
            board.make_move(move)
            score, line = self._minimax(board, max_depth - 1, -beta, -alpha, n)
            board.undo_move()

            # prepend the current move to the PV
            scored_lines.append((score, [move] + line))
            alpha = max(alpha, score)

        # keep top n lines
        top_lines = nlargest(n, scored_lines, key=lambda x: x[0])
        return top_lines


    def _minimax(self, board: Board, depth: int, alpha: float, beta: float, n: int) -> tuple[float, list[Move]]:
        if hasattr(self, "stop_event") and self.stop_event.is_set():
            raise TimeoutError()

        if depth == 0 or board.is_terminal():
            return self.eval_fn(board), []

        scored_lines = []
        for move in board.legal_moves():
            if getattr(self, "stop_event", None) and self.stop_event.is_set():
                raise TimeoutError()
            board.make_move(move)
            score, line = self._minimax(board, depth - 1, -beta, -alpha, n)
            board.undo_move()

            score = -score
            scored_lines.append((score, [move] + line))
            alpha = max(alpha, score)
            if alpha >= beta:
                break  # alpha-beta cutoff

        # keep top n lines at this node
        top_lines = nlargest(n, scored_lines, key=lambda x: x[0])
        return top_lines[0]  # return best line for parent
