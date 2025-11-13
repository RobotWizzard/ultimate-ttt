from enum import Enum

class Cell(Enum):
    X = 0
    O = 1

def other(player: Cell) -> Cell:
    if player == Cell.X:
        return Cell.O
    else:
        return Cell.X
