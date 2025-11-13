from game.cell import Cell

class SmallBoard:
    WIN_MASKS = [
        0b111_000_000, 0b000_111_000, 0b000_000_111,
        0b100_100_100, 0b010_010_010, 0b001_001_001,
        0b100_010_001, 0b001_010_100,
    ]

    def __init__(self):
        self.x_bits = 0
        self.o_bits = 0
        self.winner: Cell | None = None
        self.is_full = False
    
    def make_move(self, pos: int, player: Cell):
        mask = 1 << pos
        if (self.x_bits | self.o_bits) & mask:
            raise ValueError("Cell occupied")
        if player == Cell.X:
            self.x_bits |= mask
        else:
            self.o_bits |= mask
        self._update_status()
    
    def undo_move(self, pos: int):
        mask = 1 << pos
        self.x_bits &= ~mask
        self.o_bits &= ~mask
        self._update_status()
    
    def legal_moves_mask(self) -> int:
        return ~(self.x_bits | self.o_bits) & 0b111_111_111
    
    def _update_status(self):
        for mask in self.WIN_MASKS:
            if self.x_bits & mask == mask:
                self.winner = Cell.X
                return
            elif self.o_bits & mask == mask:
                self.winner = Cell.O
                return
        filled_mask = self.x_bits | self.o_bits
        self.is_full = filled_mask == 0b111_111_111
        self.winner = None if not self.is_full else self.winner
