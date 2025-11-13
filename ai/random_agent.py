import random
from typing import Tuple
from ai.agent import Agent
from game.board import Board

class RandomAgent(Agent):
    def choose_move(self, board: 'Board') -> Tuple[Tuple[int, int], Tuple[int, int]]:
        legal_moves = board.legal_moves()
        return random.choice(legal_moves)
    
    def calculate_lines(self, board:Board, n:int=1) -> list[tuple[float, list[tuple[tuple[int, int], tuple[int, int]]]]]:
        raise [(0.0, [])] * n
