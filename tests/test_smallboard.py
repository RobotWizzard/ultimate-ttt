import pytest
from game.cell import Cell
from game.smallboard import SmallBoard


def test_make_move_sets_bits_correctly():
    sb = SmallBoard()
    sb.make_move(0, Cell.X)
    assert sb.x_bits == 0b1
    sb.make_move(1, Cell.O)
    assert sb.o_bits == 0b10


def test_make_move_illegal_raises():
    sb = SmallBoard()
    sb.make_move(0, Cell.X)
    with pytest.raises(ValueError):
        sb.make_move(0, Cell.O)


def test_undo_move_clears_bits():
    sb = SmallBoard()
    sb.make_move(0, Cell.X)
    sb.make_move(1, Cell.O)
    sb.undo_move(0)
    assert sb.x_bits == 0
    assert sb.o_bits == 0b10
    sb.undo_move(1)
    assert sb.o_bits == 0


def test_legal_moves_mask():
    sb = SmallBoard()
    sb.make_move(0, Cell.X)
    sb.make_move(4, Cell.O)
    mask = sb.legal_moves_mask()
    # positions 0 and 4 are taken, so mask has 1s elsewhere
    taken_positions = 0b1 | 0b10000
    assert mask & taken_positions == 0
    assert mask & ~(taken_positions) == mask


def test_winner_detection_x():
    sb = SmallBoard()
    # top row: 0,1,2
    for pos in [0, 1, 2]:
        sb.make_move(pos, Cell.X)
    assert sb.winner == Cell.X
    assert not sb.is_full


def test_winner_detection_o():
    sb = SmallBoard()
    # left column: 0,3,6
    for pos in [0, 3, 6]:
        sb.make_move(pos, Cell.O)
    assert sb.winner == Cell.O
    assert not sb.is_full


def test_full_board_detection():
    sb = SmallBoard()
    moves = [
        (0, Cell.X), (1, Cell.O), (2, Cell.X),
        (3, Cell.O), (4, Cell.X), (5, Cell.O),
        (6, Cell.O), (7, Cell.X), (8, Cell.O)
    ]
    for pos, player in moves:
        sb.make_move(pos, player)
    assert sb.is_full
    # winner should be None (draw)
    assert sb.winner is None


def test_undo_after_win_resets_winner():
    sb = SmallBoard()
    # X wins top row
    for pos in [0, 1, 2]:
        sb.make_move(pos, Cell.X)
    assert sb.winner == Cell.X
    sb.undo_move(2)
    assert sb.winner is None
    assert not sb.is_full
