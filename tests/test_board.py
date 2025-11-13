import pytest
from game.cell import Cell, other
from game.board import Board
from utils.utils import encode_move, decode_move


@pytest.fixture
def empty_board():
    return Board()


def test_initial_state(empty_board):
    b = empty_board
    assert b.winner is None
    assert b.to_move == Cell.X
    assert b.active_board is None
    assert len(b.small_boards) == 9
    assert all(sb.winner is None for sb in b.small_boards)
    assert all(sb.x_bits == 0 and sb.o_bits == 0 for sb in b.small_boards)


def test_make_move_updates_board_and_turn(empty_board):
    b = empty_board
    move = encode_move(0, 0)
    b.make_move(move)

    big, small = decode_move(b.move_history[-1][0])
    assert (big, small) == (0, 0)
    sb = b.small_boards[0]
    assert sb.x_bits & (1 << 0)
    assert b.to_move == Cell.O


def test_active_board_update(empty_board):
    b = empty_board
    # move to cell 4 in small board 0 → active board = 4
    b.make_move(encode_move(0, 4))
    assert b.active_board == 4


def test_legal_moves_restricts_to_active_board(empty_board):
    b = empty_board
    b.make_move(encode_move(0, 4))
    moves = b.legal_moves()
    big_boards = {decode_move(m)[0] for m in moves}
    assert big_boards == {4}  # only active board allowed


def test_global_winner_detection(empty_board):
    b = empty_board
    # simulate top row of small boards won by X
    for i in [0, 1, 2]:
        sb = b.small_boards[i]
        sb.x_bits = 0b111_000_000  # fill top row
        sb.winner = Cell.X
    b._recompute_global_bits()
    b._update_global_winner()
    assert b.winner == Cell.X


def test_undo_move_restores_state(empty_board):
    b = empty_board
    move = encode_move(0, 0)
    b.make_move(move)
    b.undo_move()
    sb = b.small_boards[0]
    assert sb.x_bits == 0
    assert sb.o_bits == 0
    assert b.to_move == Cell.X
    assert b.active_board is None
    assert b.move_history == []


def test_copy_returns_independent_board(empty_board):
    b = empty_board
    b.make_move(encode_move(0, 0))
    b_copy = b.copy()

    # Mutate original
    b.small_boards[0].x_bits |= 1 << 1
    assert b_copy.small_boards[0].x_bits & (1 << 1) == 0  # copy unaffected
    assert b_copy.to_move == b.to_move  # copy preserves turn


def test_is_terminal_detection(empty_board):
    b = empty_board
    # Not terminal at start
    assert not b.is_terminal()

    # simulate global winner
    for i in [0, 1, 2]:
        sb = b.small_boards[i]
        sb.x_bits = 0b111_000_000
        sb.winner = Cell.X
    b._recompute_global_bits()
    b._update_global_winner()
    assert b.is_terminal()

    # Reset and fill all small boards → terminal
    b = Board()
    for sb in b.small_boards:
        sb.is_full = True
    assert b.is_terminal()
