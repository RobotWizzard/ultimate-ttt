Move = int

def index_to_coords(index:int) -> tuple[int, int]:
    """Converts indices to coordinates in (row, col)."""
    return (index // 3, index % 3)

def coords_to_index(row: int, col: int) -> int:
    """Converts coordinates in (row, col) to indices."""
    return row * 3 + col

def decode_move(i:int) -> tuple[int, int]:
    """Decodes moves from an integer consisting of big_idx << 4 | small_idx to a tuple (big_idx, small_idx)."""
    return i >> 4, i & 0b1111

def encode_move(big:int, small:int) -> int:
    """Encodes moves from a tuple to a single integer."""
    return big << 4 | small
