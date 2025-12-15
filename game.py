from enum import Enum, auto

from board import Board, DuckAgent, LEVELS

class Turn(Enum):
    PLAYER = auto()
    DUCK = auto()


class GameState(Enum):
    RUNNING = auto()
    PLAYER_WIN = auto()
    DUCK_WIN = auto()


class GameManager:
    def __init__(self, level=1):
        self.level = level
        self.board = Board(level)
        self.duck_agent = DuckAgent(self.board)
        self.turn = Turn.PLAYER
        self.state = GameState.RUNNING

    # ================= PLAYER =================
    def player_place(self, cell):
        if self.state != GameState.RUNNING or self.turn != Turn.PLAYER:
            return False

        placed = self.board.place_player_block(cell)
        if not placed:
            return False

        if not self.board.has_path_to_any_open_edge(self.board.duck_pos):
            self.state = GameState.PLAYER_WIN
            return True

        self.turn = Turn.DUCK
        return True
