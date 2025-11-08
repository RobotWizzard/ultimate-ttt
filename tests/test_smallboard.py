import pytest
from utils.cell import Cell
from game.smallboard import SmallBoard


# --- Initialization ---
def test_initial_state():
    board = SmallBoard()
    assert board.cells == [Cell.EMPTY] * 9
    assert board.winner is None
    assert board.is_full is False


# --- Coordinate conversions ---
@pytest.mark.parametrize("index,expected", [
    (0, (0, 0)), (1, (0, 1)), (2, (0, 2)),
    (3, (1, 0)), (4, (1, 1)), (5, (1, 2)),
    (6, (2, 0)), (7, (2, 1)), (8, (2, 2)),
])
def test_index_to_coords_and_back(index, expected):
    assert SmallBoard.index_to_coords(index) == expected
    assert SmallBoard.coords_to_index(*expected) == index


# --- Making moves ---
def test_make_move_updates_cell_and_status():
    board = SmallBoard()
    board._make_move(0, Cell.X)
    assert board.cells[0] == Cell.X
    assert board.winner is None
    assert not board.is_full


def test_make_move_raises_if_cell_occupied():
    board = SmallBoard()
    board._make_move(0, Cell.X)
    with pytest.raises(ValueError):
        board._make_move(0, Cell.O)


def test_make_move_using_coords():
    board = SmallBoard()
    board.make_move((1, 2), Cell.X)
    assert board.cells[5] == Cell.X


# --- Winning conditions ---
@pytest.mark.parametrize("combo", SmallBoard.WIN_COMBINATIONS)
def test_winning_combinations(combo):
    board = SmallBoard()
    for pos in combo:
        board._make_move(pos, Cell.X)
    assert board.winner == Cell.X


# --- Full board with no winner ---
def test_full_board_no_winner():
    board = SmallBoard()
    # Fill the board alternating between X and O with no win
    fill_order = [0, 1, 2, 4, 3, 5, 7, 6, 8]
    for i, pos in enumerate(fill_order):
        player = Cell.X if i % 2 == 0 else Cell.O
        board._make_move(pos, player)
    assert board.is_full
    assert board.winner is None


# --- Legal moves ---
def test_legal_moves_normal():
    board = SmallBoard()
    board._make_move(0, Cell.X)
    expected = [(0,1), (0,2), (1,0), (1,1), (1,2), (2,0), (2,1), (2,2)]
    assert sorted(board.legal_moves()) == sorted(expected)


def test_legal_moves_winner():
    board = SmallBoard()
    board._make_move(0, Cell.X)
    board._make_move(1, Cell.X)
    board._make_move(2, Cell.X)  # triggers win
    assert board.winner == Cell.X
    assert board.legal_moves() == []


def test_legal_moves_full_board():
    board = SmallBoard()
    for i in range(9):
        board._make_move(i, Cell.X if i % 2 == 0 else Cell.O)
    assert board.is_full
    assert board.legal_moves() == []
