import random
import time
from ..agent import Agent
from ..eval import simple_eval
from .mcts_node import MctsNode
from game.board import Board
from game.cell import Cell, other
from utils.utils import Move


class MctsAgent(Agent):
    def __init__(self, time_limit: float = 1.0, c: float = 1.414, use_heuristic: bool = True):
        self._args = ()
        self._kwargs = {"time_limit": time_limit, "c": c, "use_heuristic": use_heuristic}

        self.root: MctsNode | None = None
        self.time_limit = time_limit
        self.c = c
        self.use_heuristic = use_heuristic

    # ------------------------------------------------------
    # Main MCTS entry point
    # ------------------------------------------------------
    def choose_move(self, board: Board) -> Move:
        self.root = MctsNode(board)
        root = self.root
        end_time = time.time() + self.time_limit

        # ------------------------------------------------------
        # Iterations
        # ------------------------------------------------------
        while time.time() < end_time:
            node = root

            # --- SELECTION ---
            while node.is_fully_expanded() and node.children:
                node = node.best_child(c=self.c)

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
            # result: +1 = root player wins, -1 = root player loses, 0 = draw

            # --- BACKPROP ---
            self._backpropagate(node, result)

        # ------------------------------------------------------
        # Pick child with highest visit count
        # ------------------------------------------------------
        best_child = max(root.children, key=lambda c: c.visits)

        return best_child.move

    # ------------------------------------------------------
    # Rollout
    # ------------------------------------------------------
    def _rollout(self, board: Board) -> float:
        root_player = self.root.board.to_move
        current = board.copy()

        while not current.is_terminal():
            if self.use_heuristic:
                move = self.rollout_heuristic(current, current.legal_moves())
            else:
                move = random.choice(current.legal_moves())
            current.make_move(move)

        if current.winner == root_player:
            return +1
        elif current.winner == other(root_player):
            return -1
        else:
            return 0

    
    def rollout_heuristic(self, board: Board, moves: list[Move]) -> Move:
        scores = []
        root_player = self.root.board.to_move
        for move in moves:
            new_board = board.copy()
            new_board.make_move(move)
            score = simple_eval(new_board)
            if root_player == Cell.O:
                score = -score
            scores.append(score)
        best_score_idx = scores.index(max(scores))
        best_move = moves[best_score_idx]
        return best_move

    # ------------------------------------------------------
    # Backpropagation (correct perspective switching)
    # ------------------------------------------------------
    def _backpropagate(self, node: MctsNode, result: float):
        """
        result is from root player's perspective:
        +1 → root player win
        -1 → root player loss
        """
        while node is not None:
            node.visits += 1
            node.wins += result
            node = node.parent
