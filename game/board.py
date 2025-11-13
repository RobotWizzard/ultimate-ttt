from game.cell import Cell, other
from game.smallboard import SmallBoard
from utils.utils import encode_move, decode_move

class Board:
    WIN_MASKS = SmallBoard.WIN_MASKS

    def __init__(self):
        self.small_boards = [SmallBoard() for _ in range(9)]
        self.global_x = 0
        self.global_o = 0
        self.active_board: int | None = None
        self.to_move = Cell.X
        self.winner: Cell | None = None
        self.move_history: list[(int, int)] = []
        # (move, prev_active)

    def make_move(self, move: int):
        big, small = decode_move(move)
        sb = self.small_boards[big]
        sb.make_move(small, self.to_move)
        if sb.winner == Cell.X:
            self.global_x |= (1 << big)
        elif sb.winner == Cell.O:
            self.global_o |= (1 << big)

        # next active board
        prev_active = self.active_board
        next_sb = self.small_boards[small]
        if next_sb.winner or next_sb.is_full:
            self.active_board = None
        else:
            self.active_board = small

        self.move_history.append((big << 4 | small, prev_active))
        self._update_global_winner()
        self.to_move = other(self.to_move)

    def undo_move(self):
        move, prev_active = self.move_history.pop()
        big, small = decode_move(move)
        sb = self.small_boards[big]
        sb.undo_move(small)
        self.active_board = prev_active
        # recompute macroboard status
        self._recompute_global_bits()
        self._update_global_winner()
        self.to_move = other(self.to_move)

    def legal_moves(self) -> list[int]:
        moves = []
        boards_to_check = [self.active_board] if self.active_board is not None else range(9)
        for big in boards_to_check:
            sb = self.small_boards[big]
            mask = sb.legal_moves_mask()
            while mask:
                pos = (mask & -mask).bit_length() - 1  # index of lowest set bit
                moves.append(encode_move(big, pos))
                mask &= mask - 1  # clear lowest bit
        return moves

    def _update_global_winner(self):
        for mask in self.WIN_MASKS:
            if self.global_x & mask == mask:
                self.winner = Cell.X
                return
            elif self.global_o & mask == mask:
                self.winner = Cell.O
                return
        self.winner = None

    def _recompute_global_bits(self):
        self.global_x = 0
        self.global_o = 0
        for i, sb in enumerate(self.small_boards):
            if sb.winner == Cell.X:
                self.global_x |= (1 << i)
            elif sb.winner == Cell.O:
                self.global_o |= (1 << i)

    def is_terminal(self):
        return self.winner or all(sb.is_full or sb.winner for sb in self.small_boards)
    
    def copy(self):
        new = Board()
        new.global_x = self.global_x
        new.global_o = self.global_o
        new.small_boards = [SmallBoard() for _ in range(9)]
        for i in range(9):
            new.small_boards[i].x_bits = self.small_boards[i].x_bits
            new.small_boards[i].o_bits = self.small_boards[i].o_bits
            new.small_boards[i].winner = self.small_boards[i].winner
            new.small_boards[i].is_full = self.small_boards[i].is_full
        new.active_board = self.active_board
        new.to_move = self.to_move
        return new

    # def __str__(self) -> str:
    #     def cell_char(sb: SmallBoard, pos: int) -> str:
    #         if sb.x_bits & (1 << pos):
    #             return "X"
    #         elif sb.o_bits & (1 << pos):
    #             return "O"
    #         else:
    #             return "."

    #     rows = []
    #     for big_row in range(3):  # 3 rows of small boards
    #         for small_row in range(3):  # 3 rows inside each small board
    #             row_cells = []
    #             for big_col in range(3):  # 3 small boards per row
    #                 sb_index = big_row * 3 + big_col
    #                 sb = self.small_boards[sb_index]
    #                 start = small_row * 3
    #                 segment = [cell_char(sb, start + i) for i in range(3)]
    #                 row_cells.append("".join(segment))
    #             # join small boards with ' | '
    #             rows.append(" | ".join(row_cells))
    #         if big_row < 2:
    #             rows.append("------+-------+------")  # horizontal separator
    #     return "\n".join(rows)
