import torch
from pathlib import Path
from game.board import Board
from game.cell import Cell

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

def encode_small_board(sb) -> list[float]:
    """
    Encode a single SmallBoard as 16 floats:
      1.0 if X occupies cell
     -1.0 if O occupies cell
      0.0 if empty
    """
    vec = []
    for i in range(16):
        if sb.x_bits & (1 << i):
            vec.append(1.0)
        elif sb.o_bits & (1 << i):
            vec.append(-1.0)
        else:
            vec.append(0.0)
    return vec


def encode_board(board:Board) -> torch.Tensor:
    """
    Encode board as a 1D float vector suitable for neural network input.
    
    Layout:
    - 9 small boards × 16 cells = 144
    - global_x bits (9)
    - global_o bits (9)
    - active board mask (9)
    - player to move (1)
    
    Total length = 172
    """
    features = []

    # --- Small boards ---
    for sb in board.small_boards:
        features.extend(encode_small_board(sb))

    # --- Global macroboard ---
    for i in range(9):
        features.append(1.0 if board.global_x & (1 << i) else 0.0)
    for i in range(9):
        features.append(1.0 if board.global_o & (1 << i) else 0.0)

    # --- Active board (1-hot) ---
    active = [0.0] * 9
    if board.active_board is not None:
        active[board.active_board] = 1.0
    features.extend(active)

    # --- To-move ---
    features.append(1.0 if board.to_move == Cell.X else -1.0)

    return torch.tensor(features, dtype=torch.float32)

# --- Storage functions ---

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
