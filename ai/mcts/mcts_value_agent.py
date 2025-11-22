import random
import time
from typing import Optional, List
import torch
import torch.nn as nn
import torch.optim as optim

from ..agent import Agent
from .mcts_node import MctsNode
from game.board import Board
from game.cell import Cell, other
from utils.utils import Move, encode_board


# ----------------------------------------
# Simple Value Network
# ----------------------------------------
class ValueNet(nn.Module):
    def __init__(self, input_size=172, hidden=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, 1),
            nn.Tanh()  # outputs in [-1, 1]
        )

    def forward(self, x):
        return self.net(x)


# ----------------------------------------
# MCTS + Value Learning Agent
# ----------------------------------------
class MctsValueAgent(Agent):
    def __init__(
            self,
            time_limit: float = 1.0,
            learning_rate: float = 0.001,
            model_path: str = "data/models/mcts_value_agent.pt",
            replay_capacity: int = 100_000,
            batch_size: int = 256,
            c: float = 1.414
    ):
        self._args = ()
        self._kwargs = {"time_limit": time_limit, "learning_rate": learning_rate,
                        "model_path": model_path, "replay_capacity": replay_capacity,
                        "batch_size": batch_size, "c": c}
        self.root: Optional[MctsNode] = None
        self.time_limit = time_limit
        self.c = c

        # value network
        # +ve for current player win, -ve for loss
        self.model = ValueNet()
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        self.loss_fn = nn.MSELoss()

        # training / replay buffer
        self.replay_buffer: List[tuple[torch.Tensor, float]] = []
        self.replay_capacity = replay_capacity
        self.batch_size = batch_size

        self.model_path = model_path

        # try load pretrained model
        try:
            self.model.load_state_dict(torch.load(self.model_path))
            self.model.eval()
            print("[MctsValueAgent] Loaded pretrained model.")
        except FileNotFoundError:
            print("[MctsValueAgent] No pretrained model found. Creating a new model")

    # ----------------------
    # Choose move using MCTS
    # ----------------------
    def choose_move(self, board: Board) -> Move:
        self.root = MctsNode(board)
        root = self.root
        end_time = time.time() + self.time_limit

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

            # --- BACKPROPAGATION ---
            self._backpropagate(node, result)

        # pick best child
        best_child = max(root.children, key=lambda c: c.visits)
        self.root = best_child
        self.root.parent = None

        return best_child.move

    # ----------------------
    # Rollout with value network
    # ----------------------
    def _rollout(self, board: Board) -> float:
        root_player = self.root.board.to_move

        if board.is_terminal():
            if board.winner == root_player:
                return +1.0
            elif board.winner == other(root_player):
                return -1.0
            else:
                return 0.0
        
        x = encode_board(board)          # tensor [172]
        x = x.unsqueeze(0)               # [1, 172]
        self.model.eval()
        with torch.no_grad():
            v = float(self.model(x).item())
        return v

    # ----------------------
    # Backpropagation
    # ----------------------
    def _backpropagate(self, node: MctsNode, result: float):
        root_player = self.root.board.to_move
        while node is not None:
            node.visits += 1
            if node.player_just_moved == root_player:
                node.wins += result
            else:
                node.wins -= result
            node = node.parent

    # ----------------------
    # Train value network
    # ----------------------
    def _train_value_network(self, epochs: int = 1):
        if len(self.replay_buffer) < self.batch_size:
            return

        minibatch = random.sample(self.replay_buffer, self.batch_size)
        X = torch.stack([s for s, _ in minibatch], dim=0)  # shape: [batch_size, 172]
        y = torch.tensor([[v] for _, v in minibatch], dtype=torch.float32)

        self.model.train()
        for _ in range(epochs):
            self.optimizer.zero_grad()
            preds = self.model(X)
            loss = self.loss_fn(preds, y)
            loss.backward()
            self.optimizer.step()
        self.model.eval()

    # ----------------------
    # Save model to disk
    # ----------------------
    def _save_model(self):
        torch.save(self.model.state_dict(), self.model_path)

    # ----------------------
    # Self-play helper functions
    # ----------------------    
    def generate_self_play_game(self):
        board = Board()
        self.root = None
        states = []

        while not board.is_terminal():
            s = encode_board(board)
            s = s.cpu()
            states.append((s, board.to_move))

            move = self.choose_move(board)
            board.make_move(move)

        # Determine final outcome
        if board.winner == Cell.X:
            outcome = 1.0
        elif board.winner == Cell.O:
            outcome = -1.0
        else:
            outcome = 0.0

        # Convert to supervised targets
        result = []
        for s, to_move in states:
            signed = outcome if to_move == board.winner else -outcome
            result.append((s, signed))

        return result

    def add_to_replay_buffer(self, game_data):
        for s, v in game_data:
            self.replay_buffer.append((s, v))
            if len(self.replay_buffer) > self.replay_capacity:
                del self.replay_buffer[0]

    def train_from_replay(self, epochs=1):
        self._train_value_network(epochs=epochs)
