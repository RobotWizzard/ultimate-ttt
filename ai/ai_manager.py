from multiprocessing import Manager, Event, Process
from multiprocessing.synchronize import Event as EventClass
from game.board import Board
from ai import Agent
from utils.utils import Move


def _analysis_worker(board:Board, agent:Agent, output_list:list[tuple[float, list[Move]]], stop_event:EventClass, n_lines:int):
    """
    Background worker for evaluating a board using iterative deepening.
    Continuously updates the top N lines in output_list.
    """
    depth = 1
    while not stop_event.is_set():
        try:
            top_lines = agent.calculate_lines(board, depth, n=n_lines)  # top_lines: list of tuples (score, [Move, Move, ...])
            output_list[:] = top_lines
            depth += 1
        except Exception:
            break
        # Small sleep to yield to main process / UI
        stop_event.wait(0.01)


class AiManager:
    """
    Encapsulates a background AI process for board evaluation.
    Returns top N lines (PV) in real-time.
    """
    def __init__(self, board:Board, agent:Agent, n_lines:int = 2):
        self.manager = Manager()
        self.analysis = self.manager.list()  # shared list to hold top N lines
        self.stop_event = Event()
        self.board = board.copy()
        self.agent = agent
        self.n_lines = n_lines
        self.process: Process | None = None

    def start(self):
        """Start the background analysis process."""
        self.agent.stop_event = self.stop_event
        if self.process is None or not self.process.is_alive():
            self.stop_event.clear()
            self.process = Process(
                target=_analysis_worker,
                args=(self.board.copy(), self.agent, self.analysis, self.stop_event, self.n_lines),
                daemon=True
            )
            self.process.start()

    def stop(self):
        """Stop the background analysis process."""
        if self.process and self.process.is_alive():
            self.stop_event.set()
            self.process.join()
            self.process = None

    def get_analysis(self) -> list[tuple[float, list[Move]]]:
        """
        Return the current top N lines as a normal list.
        Each element is a tuple: (score, [Move, Move, ...])
        """
        return list(self.analysis)

    def update_board(self, board: Board):
        """
        Update the board for analysis (e.g., after a move has been made).
        Restarts the analysis process automatically.
        """
        self.stop()
        self.board = board.copy()
        self.start()
