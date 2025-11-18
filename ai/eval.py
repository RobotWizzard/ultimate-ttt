from game.board import Board
from game.cell import Cell
from utils.utils import count_bits

WIN_MASKS = [
    0b111_000_000, 0b000_111_000, 0b000_000_111,
    0b100_100_100, 0b010_010_010, 0b001_001_001,
    0b100_010_001, 0b001_010_100,
]

def simple_eval(board: Board) -> float:
    """Simple evaluation function for Ultimate Tic-Tac-Toe.
    Positive score = good for X, negative = good for O."""
    # --- Terminal outcomes ---
    if board.is_terminal():
        if board.winner is None:
            return 0.0
        return 100.0 if board.winner == Cell.X else -100.0

    score = 0.0

    # --- Weights ---
    SMALL_WIN = 1.0
    CENTER_BOARD_BONUS = 0.2
    CORNER_BOARD_BONUS = 0.1
    LINE2_BONUS = 0.02
    CENTER_CELL_BONUS = 0.005
    SINGLE_CELL_BONUS = 0.001

    # --- Evaluate each of the 9 small boards ---
    for i, sb in enumerate(board.small_boards):
        is_center = i == 4
        is_corner = i in (0, 2, 6, 8)

        if sb.winner == Cell.X:
            score += SMALL_WIN
            if is_center:
                score += CENTER_BOARD_BONUS
            elif is_corner:
                score += CORNER_BOARD_BONUS
            continue

        elif sb.winner == Cell.O:
            score -= SMALL_WIN
            if is_center:
                score -= CENTER_BOARD_BONUS
            elif is_corner:
                score -= CORNER_BOARD_BONUS
            continue

        # No winner yet → partial evaluation
        x_bits = sb.x_bits
        o_bits = sb.o_bits

        # Center cell bonus
        if x_bits & (1 << 4):
            score += CENTER_CELL_BONUS
        elif o_bits & (1 << 4):
            score -= CENTER_CELL_BONUS

        # Line evaluation
        for mask in WIN_MASKS:
            x = x_bits & mask
            o = o_bits & mask

            # Blocked line
            if x and o:
                continue

            x_count = count_bits(x)
            o_count = count_bits(o)

            if x_count == 2 and o_count == 0:
                score += LINE2_BONUS
            elif o_count == 2 and x_count == 0:
                score -= LINE2_BONUS
            elif x_count == 1 and o_count == 0:
                score += SINGLE_CELL_BONUS
            elif o_count == 1 and x_count == 0:
                score -= SINGLE_CELL_BONUS

    return score


def complex_eval(board: Board) -> float:
    """More complex evaluation function for Ultimate Tic-Tac-Toe.
    Positive score = good for X, negative = good for O."""
    # --- Terminal outcomes ---
    if board.is_terminal():
        if board.winner is None:
            return 0.0
        return 100.0 if board.winner == Cell.X else -100.0
    
    score = 0.0

    remaining_moves = 0
    for sb in board.small_boards:
        if sb.winner is not None or sb.is_full:
            continue
        remaining_moves += count_bits(~(sb.x_bits | sb.o_bits) & 0b111_111_111)

    # --- Weights ---
    if remaining_moves > 65:
        SMALL_WIN = 2.0
        CELL_COUNT = 0.1
        SMALL_LINE2 = 0.5
        CENTER_BONUS = 1.5
        GLOBAL_LINE2 = 1.0
        MOBILITY_BONUS = 0
    elif remaining_moves > 23:
        SMALL_WIN = 1.5
        CELL_COUNT = 0.05
        SMALL_LINE2 = 0.3
        CENTER_BONUS = 1.1
        GLOBAL_LINE2 = 2.0
        MOBILITY_BONUS = 1.0
    else:
        SMALL_WIN = 1.0
        CELL_COUNT = 0.0
        SMALL_LINE2 = 0.1
        CENTER_BONUS = 1.0
        GLOBAL_LINE2 = 3.0
        MOBILITY_BONUS = 2.0

    # --- Global board two in a row ---
    global_x = board.global_x
    global_o = board.global_o
    for mask in WIN_MASKS:
        x = global_x & mask
        o = global_o & mask
        # Blocked line
        if x and o:
            continue
        x_count = count_bits(x)
        o_count = count_bits(o)
        if x_count == 2 and o_count == 0:
            score += GLOBAL_LINE2
        elif o_count == 2 and x_count == 0:
            score -= GLOBAL_LINE2

    for i , sb in enumerate(board.small_boards):
        # --- Small board win ---
        if sb.winner == Cell.X:
            score += SMALL_WIN
        elif sb.winner == Cell.O:
            score -= SMALL_WIN
        
        x_bits = sb.x_bits
        o_bits = sb.o_bits

        # --- Cell count ---
        x_count = count_bits(x_bits)
        o_count = count_bits(o_bits)
        score += CELL_COUNT * (x_count - o_count)

        # --- Small board two in a row ---
        for mask in WIN_MASKS:
            x = x_bits & mask
            o = o_bits & mask
            # Blocked line
            if x and o:
                continue
            x_count = count_bits(x)
            o_count = count_bits(o)
            if x_count == 2 and o_count == 0:
                if (board.active_board == i or board.active_board is None) and board.to_move == Cell.X:
                    score += SMALL_WIN  # Immediate win potential
                score += SMALL_LINE2
            elif o_count == 2 and x_count == 0:
                if (board.active_board == i or board.active_board is None) and board.to_move == Cell.O:
                    score += SMALL_WIN  # Immediate win potential
                score -= SMALL_LINE2
        
        if i == 4:
            score *= CENTER_BONUS  # Center board priority

    # --- Mobility ---
    if board.active_board is None:
        if board.to_move == Cell.X:
            score += MOBILITY_BONUS 
        else:
            score -= MOBILITY_BONUS

    return score
