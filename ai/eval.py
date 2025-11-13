from game.board import Board
from game.cell import Cell

def simple_eval(board: Board) -> float:
    # --- Terminal states ---
    if board.is_terminal():
        if board.winner == Cell.X:
            return 100000
        elif board.winner == Cell.O:
            return -100000
        else:
            return 0  # draw

    score = 0

    # --- Weights ---
    SMALL_WIN = 1000
    CENTER_BOARD_BONUS = 200
    CORNER_BOARD_BONUS = 100
    LINE2_BONUS = 20
    CENTER_CELL_BONUS = 5
    SINGLE_CELL_BONUS = 1

    WIN_MASKS = [
        0b111_000_000, 0b000_111_000, 0b000_000_111,
        0b100_100_100, 0b010_010_010, 0b001_001_001,
        0b100_010_001, 0b001_010_100,
    ]

    # --- Evaluate macroboard ---
    for i, sb in enumerate(board.small_boards):
        # macroboard position bonuses
        is_center = i == 4
        is_corner = i in (0, 2, 6, 8)

        if sb.winner == Cell.X:
            score += SMALL_WIN
            if is_center:
                score += CENTER_BOARD_BONUS
            elif is_corner:
                score += CORNER_BOARD_BONUS
        elif sb.winner == Cell.O:
            score -= SMALL_WIN
            if is_center:
                score -= CENTER_BOARD_BONUS
            elif is_corner:
                score -= CORNER_BOARD_BONUS
        else:
            # evaluate unfinished small board
            x = sb.x_bits
            o = sb.o_bits

            # center cell bonus
            if x & (1 << 4):
                score += CENTER_CELL_BONUS
            elif o & (1 << 4):
                score -= CENTER_CELL_BONUS

            # partial line evaluation
            for mask in WIN_MASKS:
                x_count = bin(mask & x).count("1")
                o_count = bin(mask & o).count("1")
                if x_count > 0 and o_count > 0:
                    continue  # blocked
                if x_count == 2 and o_count == 0:
                    score += LINE2_BONUS
                elif o_count == 2 and x_count == 0:
                    score -= LINE2_BONUS
                elif x_count == 1 and o_count == 0:
                    score += SINGLE_CELL_BONUS
                elif o_count == 1 and x_count == 0:
                    score -= SINGLE_CELL_BONUS

    return score / 100

