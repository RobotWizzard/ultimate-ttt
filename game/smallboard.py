from typing import List, Optional, Tuple
from utils.cell import Cell, other


class SmallBoard:
    # 0 1 2
    # 3 4 5
    # 6 7 8
    # position = (row, col), (0,0) is top-left
    WIN_COMBINATIONS = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
                        (0, 3, 6), (1, 4, 7), (2, 5, 8),
                        (0, 4, 8), (2, 4, 6)]

    def __init__(self):
        self.cells: List[Cell] = [Cell.EMPTY] * 9
        self.winner: Optional[Cell] = None
        self.is_full: bool = False
    
    @staticmethod
    def index_to_coords(index: int) -> Tuple[int, int]:
        return (index // 3, index % 3)
    
    @staticmethod
    def coords_to_index(row: int, col: int) -> int:
        return row * 3 + col
    
    def _make_move(self, position: int, player: Cell):
        if self.cells[position] != Cell.EMPTY:
            raise ValueError("Cell is already occupied")
        self.cells[position] = player
        self._update_status()
    
    def make_move(self, position: Tuple[int, int], player: Cell):
        self._make_move(self, self.coords_to_index(position[0], position[1]), player)
    
    def legal_moves(self) -> List[Tuple[int, int]]:
        if self.winner is not None or self.is_full:
            return []
        return [self.index_to_coords(i) for i in range(9) if self.cells[i] == Cell.EMPTY]
    
    def _update_status(self):
        for combo in self.WIN_COMBINATIONS:
            if (self.cells[combo[0]] != Cell.EMPTY and
                self.cells[combo[0]] == self.cells[combo[1]] == self.cells[combo[2]]):
                self.winner = self.cells[combo[0]]
                break
        if all(cell != Cell.EMPTY for cell in self.cells):
            self.is_full = True
