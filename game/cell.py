from enum import Enum

class Cell(Enum):
    EMPTY = 0
    X = 1
    O = 2

def other(player: Cell) -> Cell:
    if player == Cell.X:
        return Cell.O
    elif player == Cell.O:
        return Cell.X
    else:
        raise ValueError("No other player for EMPTY cell")