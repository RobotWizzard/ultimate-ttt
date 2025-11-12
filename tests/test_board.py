import pytest
from utils.cell import Cell
from game.smallboard import SmallBoard
from game.board import Board
from utils.cell import other


# --- Initialization ---
def test_initial_state():
    b = Board()
    assert len(b.boards) == 9
    assert all(isinstance(sb, SmallBoard) for sb in b.boards)
    assert b.global_board == [Cell.EMPTY] * 9
    assert b.active_board is None
    assert b.to_move == Cell.X
    assert b.winner is None


# --- Coordinate conversions ---
@pytest.mark.parametrize("index,expected", [
    (0, (0, 0)), (1, (0, 1)), (2, (0, 2)),
    (3, (1, 0)), (4, (1, 1)), (5, (1, 2)),
    (6, (2, 0)), (7, (2, 1)), (8, (2, 2)),
])
def test_index_to_coords_and_back(index, expected):
    assert Board.index_to_coords(index) == expected
    assert Board.coords_to_index(*expected) == index


# --- Move mechanics ---
def test_make_move_basic():
    b = Board()
    b._make_move(0, 4)  # play in top-left board, center cell
    sb = b.boards[0]
    assert sb.cells[4] == Cell.X
    assert b.to_move == Cell.O
    assert b.active_board == 4  # next player must play in board 4


def test_make_move_enforces_active_board():
    b = Board()
    b._make_move(0, 4)
    with pytest.raises(ValueError):
        b._make_move(1, 0)  # must play in board 4 now


def test_make_move_sets_active_none_when_target_full():
    b = Board()
    # pretend board 4 (target) is full
    b.boards[4].is_full = True
    b._make_move(0, 4)
    assert b.active_board is None


def test_make_move_updates_global_board_when_smallboard_wins():
    b = Board()
    # simulate a win in board 0
    sb = b.boards[0]
    sb.winner = Cell.X
    b.global_board[0] = Cell.X
    b._make_move(0, 4)
    assert b.global_board[0] == Cell.X


# --- Global winner detection ---
def test_check_winner_detects_three_in_a_row():
    b = Board()
    b.global_board[0] = b.global_board[1] = b.global_board[2] = Cell.X
    assert b._check_winner() == (Cell.X, (0, 1, 2))

def test_check_winner_returns_none_if_no_winner():
    b = Board()
    b.global_board[0] = Cell.X
    b.global_board[1] = Cell.O
    assert b._check_winner() == (None, None)


# --- Legal moves ---
def test_legal_moves_any_board_initial():
    b = Board()
    moves = b.legal_moves()
    assert len(moves) == 9 * 9
    assert ((0, 0), (0, 0)) in moves

def test_legal_moves_only_active_board():
    b = Board()
    b.active_board = 4
    moves = b.legal_moves()
    assert all(big == (1, 1) for big, _ in moves)


def test_legal_moves_excludes_won_and_full_boards():
    b = Board()
    b.boards[0].winner = Cell.X
    b.boards[1].is_full = True
    moves = b.legal_moves()
    # boards 0 and 1 should not appear
    assert all(Board.coords_to_index(*big) not in (0, 1) for big, _ in moves)


# --- Terminal state ---
def test_is_terminal_when_winner():
    b = Board()
    b.winner = Cell.X
    assert b.is_terminal()

def test_is_terminal_when_all_boards_finished():
    b = Board()
    for sb in b.boards:
        sb.is_full = True
    assert b.is_terminal()

def test_is_not_terminal_while_boards_open():
    b = Board()
    b.boards[0].is_full = True
    assert not b.is_terminal()


# --- Undo move ---
def test_undo_move_restores_state():
    b = Board()
    b._make_move(0, 0)
    prev_to_move = b.to_move
    b.undo_move()
    assert b.to_move == other(prev_to_move)
    assert b.boards[0].cells[0] == Cell.EMPTY
    assert len(b.move_history) == 0


# --- Copy behavior ---
def test_copy_creates_independent_clone():
    b1 = Board()
    b1._make_move(0, 0)
    b2 = b1.copy()
    assert b1 is not b2
    assert b1.boards[0] is not b2.boards[0]
    assert b1.boards[0].cells == b2.boards[0].cells
    # mutate clone and ensure original unchanged
    b2.boards[0].cells[0] = Cell.O
    assert b1.boards[0].cells[0] != Cell.O


# --- String representation ---
def test_str_contains_grid_lines_and_symbols():
    b = Board()
    s = str(b)
    assert isinstance(s, str)
    assert '|' in s
    assert '-' in s
    assert s.count('.') == 9 * 9
