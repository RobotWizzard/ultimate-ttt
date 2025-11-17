import time
from heapq import nlargest, nsmallest
from typing import List, Tuple, Optional

from .agent import Agent
from game.board import Board
from game.cell import Cell
from utils.utils import Move


ScorePV = Tuple[float, List[Move]]


class MinimaxAgent(Agent):
    INF = 1e9

    def __init__(self, eval_fn: callable, time_limit: float = 1.0):
        """
        eval_fn(board) -> float
          * should return positive = good for X, negative = good for O
        time_limit: seconds used by choose_move for iterative deepening
        """
        # store args for multiprocessing factories
        self._args = (eval_fn,)
        self._kwargs = {"time_limit": time_limit}

        self.eval_fn = eval_fn
        self.time_limit = time_limit

        # Used by AiManager to interrupt search:
        # AiManager must set agent.stop_event = some multiprocessing.Event() or threading.Event()
        # and call event.set() to request stop.
        self.stop_event = None  # injected externally

        # remembers best PV from previous completed depth (used for move ordering)
        self.last_root_pv: List[Move] = []

        # cache of last fully-completed root lines (useful for choose_move fallback)
        self.last_completed_lines: List[ScorePV] = []

    # ------------------------------------------
    # Public API
    # ------------------------------------------
    def choose_move(self, board: Board) -> Optional[Move]:
        """
        Iterative deepening driver. Returns best move found within time_limit.
        If interrupted, returns the best move from the last fully-completed depth.
        """
        start_time = time.time()
        deadline = start_time + self.time_limit

        # reset last_root_pv for move ordering
        self.last_root_pv = []
        self.last_completed_lines = []

        depth = 1
        best_move: Optional[Move] = None

        while True:
            # time check prior to launching deeper search
            if time.time() >= deadline:
                break

            # attach a small time guard to allow _minimax to exit quickly
            try:
                # run a single-depth search that returns top-1 root lines
                lines = self.calculate_lines(board, depth, n=1)
            except TimeoutError:
                # interrupted during deeper search -> keep last completed
                break

            if lines:
                # lines: list[(score, pv)]
                self.last_completed_lines = lines
                best_move = lines[0][1][0] if lines[0][1] else None
                # update last_root_pv for move ordering next iteration
                self.last_root_pv = lines[0][1]
            depth += 1

            # small time check before next depth (avoid starting huge depth with no time)
            if time.time() >= deadline:
                break

        return best_move

    def calculate_lines(self, board: Board, max_depth: int, n: int = 1) -> List[ScorePV]:
        """
        Compute top-n PV lines at the root using minimax + alpha-beta.
        This function explores root moves (with simple ordering) and calls _minimax
        which returns a single (score, pv) per child; we negate child scores to parent's perspective.
        """
        if getattr(self, "stop_event", None) and self.stop_event.is_set():
            raise TimeoutError()

        scored_lines: List[ScorePV] = []

        # Get legal moves
        legal = list(board.legal_moves())

        # Simple move ordering at root: try PV move first if available
        ordered_moves = self._order_root_moves(legal)

        alpha = -self.INF
        beta = self.INF

        for move in ordered_moves:
            if getattr(self, "stop_event", None) and self.stop_event.is_set():
                raise TimeoutError()

            board.make_move(move)
            try:
                child_score, child_pv = self._minimax(board, max_depth - 1, -beta, -alpha)
            except TimeoutError:
                board.undo_move()
                raise
            board.undo_move()

            pv = [move] + child_pv
            scored_lines.append((child_score, pv))

            # update alpha for root-based move ordering / pruning
            alpha = max(alpha, child_score)

        if board.to_move == Cell.X:
            top_lines = nlargest(n, scored_lines, key=lambda x: x[0])
        else:
            top_lines = nsmallest(n, scored_lines, key=lambda x: x[0])
        return top_lines

    # ------------------------------------------
    # Core minimax / negamax implementation (returns single best (score, pv) for node)
    # ------------------------------------------
    def _minimax(self, board: Board, depth: int, alpha: float, beta: float) -> ScorePV:
        """
        Returns tuple (best_score, best_pv_list) from the perspective of the node (side to move).
        best_score is the value for the current player (positive = good for current player).
        """

        # interrupt check
        if getattr(self, "stop_event", None) and self.stop_event.is_set():
            raise TimeoutError()

        # Terminal / leaf
        if depth == 0 or board.is_terminal():
            # Our eval_fn returns positive for X; convert to current-player perspective:
            # If it's X to move, eval_for_current = eval_fn(board)
            # If it's O to move, eval_for_current = -eval_fn(board)
            raw = self.eval_fn(board)
            eval_for_current = raw if board.to_move == Cell.X else -raw
            return eval_for_current, []

        best_score = -self.INF
        best_pv: List[Move] = []

        # Move ordering: try PV move first, then others
        moves = list(board.legal_moves())
        moves = self._order_moves(moves)

        for move in moves:
            if getattr(self, "stop_event", None) and self.stop_event.is_set():
                raise TimeoutError()

            board.make_move(move)
            child_score, child_pv = self._minimax(board, depth - 1, -beta, -alpha)
            board.undo_move()

            child_score = -child_score  # negamax inversion to current node's perspective

            # Update best
            if child_score > best_score:
                best_score = child_score
                best_pv = [move] + child_pv

            alpha = max(alpha, child_score)
            if alpha >= beta:
                # cutoff
                break

        return best_score, best_pv

    # ------------------------------------------
    # Move ordering helpers
    # ------------------------------------------
    def _order_root_moves(self, legal_moves: List[Move]) -> List[Move]:
        """
        Order root moves. Try last iteration's PV move first (if present),
        then keep remaining moves as-is.
        """
        if not self.last_root_pv:
            return legal_moves

        pv0 = self.last_root_pv[0]
        ordered = []
        # try to put pv0 first if it's legal
        if pv0 in legal_moves:
            ordered.append(pv0)
        # append rest preserving original order, skipping pv0 if already added
        for m in legal_moves:
            if m != pv0:
                ordered.append(m)
        return ordered

    def _order_moves(self, moves: List[Move]) -> List[Move]:
        """
        Non-root ordering used inside recursion.
        For now we only try a tiny heuristic: if the last_root_pv suggests a continuation,
        prefer that move when the small board / move matches position in last_root_pv.
        This is cheap and improves pruning a bit.
        """
        if not self.last_root_pv:
            return moves
        # build a set of pv moves for fast check
        pv_set = set(self.last_root_pv)
        # prefer PV moves first
        pv_moves = [m for m in moves if m in pv_set]
        other_moves = [m for m in moves if m not in pv_set]
        return pv_moves + other_moves
