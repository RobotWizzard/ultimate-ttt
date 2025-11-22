from typing import Optional
from utils.utils import Move
from game.board import Board
from game.cell import Cell, other


class MctsNode:
    def __init__(self, board: Board, parent: Optional['MctsNode'] = None, move: Optional[Move] = None):
        self.board = board
        self.parent = parent
        self.move = move
        self.player_just_moved = other(board.to_move)

        # MCTS stats
        self.children: list[MctsNode] = []
        self.visits = 0
        self.wins = 0.0

        # moves not yet explored
        self.untried_moves = board.legal_moves()

    # ------------------------------------------------------
    # Node helpers
    # ------------------------------------------------------
    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def best_child(self, c=1.414):
        from math import sqrt, log
        return max(
            self.children,
            key=lambda child: (
                child.wins / child.visits
                + c * sqrt(log(self.visits + 1) / (child.visits + 1))
            )
        )
