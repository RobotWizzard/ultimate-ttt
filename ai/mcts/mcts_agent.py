import random
import time
from ..agent import Agent
from .mcts_node import MctsNode
from game.board import Board
from game.cell import Cell
from utils.utils import Move


class MctsAgent(Agent):
    def __init__(self, time_limit: float = 0.5):
        self.root: MctsNode | None = None
        self.time_limit = time_limit

    # ------------------------------------------------------
    # Root handling (persistent tree)
    # ------------------------------------------------------
    def _set_root(self, board: Board):
        """Ensure self.root corresponds to the given board state."""

        if not board.move_history:
            self.root = MctsNode(board)
            return

        if self.root is not None:
            last_move = board.move_history[-1]
            for child in self.root.children:
                if child.move == last_move:
                    self.root = child
                    self.root.parent = None
                    return

        self.root = MctsNode(board)

    # ------------------------------------------------------
    # Main MCTS entry point
    # ------------------------------------------------------
    def choose_move(self, board: Board) -> Move:
        # attach root to current state
        self._set_root(board)

        root = self.root
        end_time = time.time() + self.time_limit

        # ------------------------------------------------------
        # Iterations
        # ------------------------------------------------------
        while time.time() < end_time:
            node = root

            # --- SELECTION ---
            while node.is_fully_expanded() and node.children:
                node = node.best_child()

            # --- EXPANSION ---
            if node.untried_moves:
                move = random.choice(node.untried_moves)
                node.untried_moves.remove(move)

                new_board = node.board.copy()
                new_board.make_move(move)

                child_node = MctsNode(new_board, parent=node, move=move)
                node.children.append(child_node)
                node = child_node

            # --- SIMULATION ---
            result = self._rollout(node.board)
            # result: +1 = X wins, -1 = O wins

            # --- BACKPROP ---
            self._backpropagate(node, result)

        # ------------------------------------------------------
        # Pick child with highest visit count
        # ------------------------------------------------------
        best_child = max(root.children, key=lambda c: c.visits)

        # Persist tree
        self.root = best_child
        self.root.parent = None

        return best_child.move

    # ------------------------------------------------------
    # Rollout
    # ------------------------------------------------------
    def _rollout(self, board: Board) -> float:
        current = board.copy()

        while not current.is_terminal():
            move = random.choice(current.legal_moves())
            current.make_move(move)

        # Return reward from X perspective
        if current.winner == Cell.X:
            return +1.0
        elif current.winner == Cell.O:
            return -1.0
        else:
            return 0.0

    # ------------------------------------------------------
    # Backpropagation (correct perspective switching)
    # ------------------------------------------------------
    def _backpropagate(self, node: MctsNode, result: float):
        """
        result is from X's perspective:
        +1 → X win
        -1 → O win

        Backprop alternates sign each level.
        """
        while node is not None:
            node.visits += 1
            node.wins += result

            result = -result  # flip perspective for parent
            node = node.parent
