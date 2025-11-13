from game.board import Board
from game.cell import Cell, other

def simple_eval(board: Board) -> float:
    if board.is_terminal():
        if board.winner is None:
            return 0  # draw
        return 100000 if board.winner == board.to_move else -100000

    score = 0

    # --- Weights ---
    SMALL_WIN = 1000
    CENTER_BOARD_BONUS = 200
    CORNER_BOARD_BONUS = 100
    LINE2_BONUS = 20
    CENTER_CELL_BONUS = 5
    SINGLE_CELL_BONUS = 1

    # Precomputed small board win masks
    WIN_MASKS = [
        0b111_000_000, 0b000_111_000, 0b000_000_111,
        0b100_100_100, 0b010_010_010, 0b001_001_001,
        0b100_010_001, 0b001_010_100,
    ]

    player = board.to_move
    opponent = Cell.O if player == Cell.X else Cell.X

    # --- Evaluate each small board ---
    for i, sb in enumerate(board.small_boards):
        is_center = i == 4
        is_corner = i in (0, 2, 6, 8)

        if sb.winner == player:
            score += SMALL_WIN
            if is_center:
                score += CENTER_BOARD_BONUS
            elif is_corner:
                score += CORNER_BOARD_BONUS
        elif sb.winner == opponent:
            score -= SMALL_WIN
            if is_center:
                score -= CENTER_BOARD_BONUS
            elif is_corner:
                score -= CORNER_BOARD_BONUS
        else:
            # Player/Opponent bits
            player_bits = sb.x_bits if player == Cell.X else sb.o_bits
            opp_bits = sb.o_bits if player == Cell.X else sb.x_bits
            empty_mask = ~(player_bits | opp_bits) & 0b111_111_111

            # Center cell bonus
            center_mask = 1 << 4
            if player_bits & center_mask:
                score += CENTER_CELL_BONUS
            elif opp_bits & center_mask:
                score -= CENTER_CELL_BONUS

            # --- Partial lines evaluation ---
            for mask in WIN_MASKS:
                p = player_bits & mask
                o = opp_bits & mask

                if p and o:
                    continue  # blocked
                if p == mask >> 0b111:  # Not needed, simplified below
                    pass

                # Count bits using Kernighan's algorithm
                def count_bits(x):
                    cnt = 0
                    while x:
                        x &= x - 1
                        cnt += 1
                    return cnt

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

    return score / 100
