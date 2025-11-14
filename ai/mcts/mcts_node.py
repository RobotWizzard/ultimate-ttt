from typing import Optional
from utils.utils import Move
from game.board import Board
from game.cell import Cell


class MctsNode:
    def __init__(self, board: Board, parent: Optional['MctsNode'] = None, move: Optional[Move] = None):
        self.board = board
        self.parent = parent
        self.move = move

        if parent is None:
            # Root node: no move created this, so just set opposite of board.to_move
            # Root represents the state BEFORE any move by this agent
            self.player_just_moved = Cell.O if board.to_move == Cell.X else Cell.X
        else:
            # Parent's board.to_move becomes "player_just_moved" for this node
            self.player_just_moved = parent.board.to_move

        # MCTS stats
        self.children: list[MctsNode] = []
        self.visits = 0
        self.wins = 0.0  # score accumulated for "player_just_moved"

        # moves not yet explored
        self.untried_moves = list(board.legal_moves())

    # ------------------------------------------------------
    # Node helpers
    # ------------------------------------------------------
    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def best_child(self, c_param=1.4):
        from math import sqrt, log
        return max(
            self.children,
            key=lambda child: (
                child.wins / child.visits
                + c_param * sqrt(log(self.visits + 1) / (child.visits + 1))
            )
        )
