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

def test_legal_moves_skips_won_boards(empty_board):
    board = empty_board

    # Make some moves to win small board 0 for X
    sb0_moves = [0, 3, 1, 4, 2]  # X will win top row
    player = Cell.X
    for pos in sb0_moves:
        board.make_move(encode_move(0, pos))
        player = Cell.O if player == Cell.X else Cell.X
        board.to_move = player

    # Active board is None so it would normally include all boards
    board.active_board = None
    moves = board.legal_moves()

    # Check that no move is in board 0 (already won)
    for move in moves:
        big, small = decode_move(move)
        assert big != 0

    # Check that moves are only from boards that are not full/won
    for big in range(1, 9):
        sb = board.small_boards[big]
        mask = sb.legal_moves_mask()
        for move in moves:
            b, s = decode_move(move)
            if b == big:
                assert mask & (1 << s)


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

def test_copy_returns_identical_board(empty_board):
    b = empty_board
    moves = [encode_move(0, 0), encode_move(0, 1), encode_move(1, 0)]
    for move in moves:
        b.make_move(move)
    b_copy = b.copy()

    # Check all attributes are identical
    b_copy.global_o == b.global_o
    b_copy.global_x == b.global_x
    assert b_copy.to_move == b.to_move
    assert b_copy.active_board == b.active_board
    assert b_copy.winner == b.winner
    assert b_copy.move_history == b.move_history
    for i in range(9):
        sb_orig = b.small_boards[i]
        sb_copy = b_copy.small_boards[i]
        assert sb_orig.x_bits == sb_copy.x_bits
        assert sb_orig.o_bits == sb_copy.o_bits
        assert sb_orig.winner == sb_copy.winner
        assert sb_orig.is_full == sb_copy.is_full


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
