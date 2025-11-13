from game.board import Board
from game.cell import Cell

def simple_eval(board:Board) -> float:
    # --- Terminal states ---
    if board.is_terminal():
        if board.winner == Cell.X:
            return 100000
        elif board.winner == Cell.O:
            return -100000
        else:
            return 0  # draw

    score = 0

    # --- Weights for different features ---
    SMALL_WIN = 1000
    CENTER_BOARD_BONUS = 200
    CORNER_BOARD_BONUS = 100
    LINE2_BONUS = 20   # partial progress in small boards
    CENTER_CELL_BONUS = 5

    # --- Macroboard evaluation (small board wins) ---
    for i in range(9):
        owner = board.global_board[i]

        # board position (0–8)
        is_center = i == 4
        is_corner = i in (0, 2, 6, 8)

        # Full small board won
        if owner == Cell.X:
            score += SMALL_WIN
            if is_center:
                score += CENTER_BOARD_BONUS
            elif is_corner:
                score += CORNER_BOARD_BONUS
        elif owner == Cell.O:
            score -= SMALL_WIN
            if is_center:
                score -= CENTER_BOARD_BONUS
            elif is_corner:
                score -= CORNER_BOARD_BONUS
        else:
            # --- Evaluate unfinished small boards ---
            sb = board.boards[i]
            cells = sb.cells

            # Center cell slightly valuable
            if cells[4] == Cell.X:
                score += CENTER_CELL_BONUS
            elif cells[4] == Cell.O:
                score -= CENTER_CELL_BONUS

            # Look at all winning lines within this small board
            for a, b, c in Board.WIN_COMBINATIONS:
                line = [cells[a], cells[b], cells[c]]
                if Cell.X in line and Cell.O in line:
                    continue  # blocked
                x_count = line.count(Cell.X)
                o_count = line.count(Cell.O)
                if x_count == 2 and o_count == 0:
                    score += LINE2_BONUS
                elif o_count == 2 and x_count == 0:
                    score -= LINE2_BONUS
                elif x_count == 1 and o_count == 0:
                    score += 5
                elif o_count == 1 and x_count == 0:
                    score -= 5

    return score / 100
