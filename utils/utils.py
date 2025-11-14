# --- Types ---

Move = int

# --- General utility ---

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

# --- Storage functions ---

from pathlib import Path
from game.board import Board

def save_game(board: Board, folder: str = "data/saved_games", filename: str = None):
    """Save a completed game to a txt file."""
    if not board.is_terminal():
        raise ValueError("Cannot save incomplete game")

    folder_path = Path(folder)
    folder_path.mkdir(exist_ok=True, parents=True)

    if filename is None:
        filename = f"game_{len(list(folder_path.glob('*.txt'))) + 1}.txt"

    path = folder_path / filename
    with open(path, "w") as f:
        for move, _ in board.move_history:
            f.write(str(move))
        f.write("\n")
        f.write(f"{board.winner.value if board.winner else 'Draw'}\n")

    return path

def load_game(path: str) -> Board:
    """Load a saved game from txt file."""
    with open(path, "r") as f:
        lines = f.read().splitlines()

    board = Board()
    for char in lines[0]:
        move = decode_move(int(char))
        board.make_move(move)

    return board

def list_saved_games(folder: str = "data/saved_games") -> list[str]:
    folder_path = Path(folder)
    return [f.name for f in folder_path.glob("*.txt")]
