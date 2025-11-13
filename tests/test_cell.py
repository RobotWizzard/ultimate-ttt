import pytest
from game.cell import Cell, other

def test_other_function():
    assert other(Cell.X) == Cell.O
    assert other(Cell.O) == Cell.X
