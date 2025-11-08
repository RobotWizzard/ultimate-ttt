import random
from typing import Tuple
from ai.agent import Agent
from game.board import Board

class RandomAgent(Agent):
    def choose_move(self, board: 'Board') -> Tuple[Tuple[int, int], Tuple[int, int]]:
        legal_moves = board.legal_moves()
        return random.choice(legal_moves)
