import pytest
import random
from ai.random_agent import RandomAgent


class DummyBoard:
    def __init__(self):
        self._moves = [
            ((0, 0), (1, 1)),
            ((0, 2), (2, 2)),
            ((1, 1), (0, 0)),
        ]
        self.called = False

    def legal_moves(self):
        self.called = True
        return self._moves


def test_choose_move_returns_valid_move(monkeypatch):
    agent = RandomAgent()
    board = DummyBoard()

    # Make randomness deterministic for test repeatability
    monkeypatch.setattr(random, "choice", lambda seq: seq[1])

    move = agent.choose_move(board)

    assert board.called, "Agent must call legal_moves()"
    assert move in board._moves, "Move must come from legal_moves()"


def test_choose_move_randomness(monkeypatch):
    agent = RandomAgent()
    board = DummyBoard()

    # Patch random.choice to count calls
    called = {}

    def fake_choice(seq):
        called["yes"] = True
        return seq[0]

    monkeypatch.setattr(random, "choice", fake_choice)
    agent.choose_move(board)
    assert "yes" in called
