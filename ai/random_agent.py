import random
from typing import Tuple
from ai.agent import Agent
from game.board import Board
from utils.utils import Move

class RandomAgent(Agent):
    def choose_move(self, board: 'Board') -> Move:
        legal_moves = board.legal_moves()
        return random.choice(legal_moves)
    
    def calculate_lines(self, board:Board, n:int=1) -> list[tuple[float, list[Move]]]:
        return [(0.0, [])] * n
