import pytest
from utils.utils import index_to_coords, coords_to_index, encode_move, decode_move


@pytest.mark.parametrize("index", range(9))
def test_index_to_coords_and_back(index):
    row, col = index_to_coords(index)
    assert coords_to_index(row, col) == index


@pytest.mark.parametrize("row,col", [(0,0), (0,1), (1,0), (2,2), (2,1)])
def test_coords_to_index_and_back(row, col):
    index = coords_to_index(row, col)
    r, c = index_to_coords(index)
    assert (r, c) == (row, col)


@pytest.mark.parametrize("big,small", [(0,0), (1,2), (8,8), (3,5), (7,0)])
def test_encode_decode_move(big, small):
    move = encode_move(big, small)
    b, s = decode_move(move)
    assert (b, s) == (big, small)


def test_encode_move_values():
    # Check that encoding produces the expected integer
    assert encode_move(0, 0) == 0
    assert encode_move(1, 1) == 0x11
    assert encode_move(2, 3) == (2 << 4 | 3)
    assert encode_move(8, 8) == (8 << 4 | 8)


def test_decode_move_values():
    # Check that decoding produces the correct big and small indices
    assert decode_move(0) == (0, 0)
    assert decode_move(0x11) == (1, 1)
    assert decode_move((2 << 4 | 3)) == (2, 3)
    assert decode_move((8 << 4 | 8)) == (8, 8)
