from game.board import Board
from game.cell import Cell, other

def simple_eval(board: Board) -> float:
    # --- Terminal outcomes ---
    if board.is_terminal():
        if board.winner is None:
            return 0.0
        return 1.0 if board.winner == board.to_move else -1.0

    score = 0.0

    # --- Scaled Weights (sum cannot exceed ~1.0) ---
    SMALL_WIN = 0.20
    CENTER_BOARD_BONUS = 0.05
    CORNER_BOARD_BONUS = 0.03
    LINE2_BONUS = 0.01
    CENTER_CELL_BONUS = 0.003
    SINGLE_CELL_BONUS = 0.001

    WIN_MASKS = [
        0b111_000_000, 0b000_111_000, 0b000_000_111,
        0b100_100_100, 0b010_010_010, 0b001_001_001,
        0b100_010_001, 0b001_010_100,
    ]

    player = board.to_move
    opponent = Cell.O if player == Cell.X else Cell.X

    # --- Evaluate each of the 9 small boards ---
    for i, sb in enumerate(board.small_boards):
        is_center = i == 4
        is_corner = i in (0, 2, 6, 8)

        if sb.winner == player:
            score += SMALL_WIN
            if is_center:
                score += CENTER_BOARD_BONUS
            elif is_corner:
                score += CORNER_BOARD_BONUS
            continue

        elif sb.winner == opponent:
            score -= SMALL_WIN
            if is_center:
                score -= CENTER_BOARD_BONUS
            elif is_corner:
                score -= CORNER_BOARD_BONUS
            continue

        # No winner yet → partial evaluation
        player_bits = sb.x_bits if player == Cell.X else sb.o_bits
        opp_bits = sb.o_bits if player == Cell.X else sb.x_bits

        # Center cell bonus
        if player_bits & (1 << 4):
            score += CENTER_CELL_BONUS
        elif opp_bits & (1 << 4):
            score -= CENTER_CELL_BONUS

        # Helper
        def count_bits(x):
            c = 0
            while x:
                x &= x - 1
                c += 1
            return c

        # Line evaluation
        for mask in WIN_MASKS:
            p = player_bits & mask
            o = opp_bits & mask

            # Blocked line
            if p and o:
                continue

            p_count = count_bits(p)
            o_count = count_bits(o)

            if p_count == 2 and o_count == 0:
                score += LINE2_BONUS
            elif o_count == 2 and p_count == 0:
                score -= LINE2_BONUS
            elif p_count == 1 and o_count == 0:
                score += SINGLE_CELL_BONUS
            elif o_count == 1 and p_count == 0:
                score -= SINGLE_CELL_BONUS

    # Clamp to [-1, 1] for safety
    if score > 1.0:
        score = 1.0
    elif score < -1.0:
        score = -1.0

    return score

