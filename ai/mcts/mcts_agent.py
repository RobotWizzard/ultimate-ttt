import random
import time
from ..agent import Agent
from .mcts_node import MctsNode
from game.board import Board
from game.cell import Cell, other
from utils.utils import Move


class MctsAgent(Agent):
    def __init__(self, time_limit: float = 1.0, c: float = 1.414, use_heuristic: bool = True, persistent_tree: bool = True):
        self.root: MctsNode | None = None
        self.time_limit = time_limit
        self.c = c
        self.use_heuristic = use_heuristic
        self.persistent_tree = persistent_tree
    
    def _set_root(self, board: Board):
        if not self.persistent_tree:
            self.root = MctsNode(board)
            return
        
        if self.root is None:
            self.root = MctsNode(board)
            return

        if board.move_history:
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
            # result: +1 = X wins, -1 = O wins

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
            move = random.choice(current.legal_moves())
            current.make_move(move)

        if current.winner == root_player:
            return +1
        elif current.winner == other(root_player):
            return -1
        else:
            return 0

    
    def rollout_heuristic(self, board: Board, moves: list[Move]) -> Move:
        # Prioritize winning moves
        for move in moves:
            new_board = board.copy()
            new_board.make_move(move)
            if new_board.winner == board.to_move:
                return move  # Immediate win
        
        # If move causes opponent to win next, avoid it
        save_moves = []
        opponent = other(board.to_move)
        for move in moves:
            new_board = board.copy()
            new_board.make_move(move)
            opponent_wins = False
            for opp_move in new_board.legal_moves():
                new_board.make_move(opp_move)
                if new_board.winner == opponent:
                    opponent_wins = True
                new_board.undo_move()
                if opponent_wins:
                    break  # This move allows opponent to win
            new_board.undo_move()
            if not opponent_wins:
                save_moves.append(move)

        # Block opponent winning move
        # opponent = other(board.to_move)
        # for move in save_moves:
        #     new_board = board.copy()
        #     new_board.to_move = opponent
        #     new_board.make_move(move)
        #     if new_board.winner == opponent:
        #         return move  # Block opponent

        # Otherwise, moves in the center board (Interestingly, this makes performance worse)
        # center_moves = [m for m in moves if m >> 4 == 4]
        # if center_moves:
        #     return random.choice(center_moves)

        # Fallback: pick random
        return random.choice(moves)

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
