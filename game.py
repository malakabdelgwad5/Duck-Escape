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
        self.duck_moved = False
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
        self.duck_moved = False

        
        return True


# Duck take turn in game by Malak abd elgwad
    # ================= DUCK =================
    def duck_take_turn(self):
        if self.state != GameState.RUNNING or self.turn != Turn.DUCK:
            return None

        nxt = self.duck_agent.next_step_towards_nearest_edge()

        if nxt is None:
            if self.board.duck_on_edge():
                self.state = GameState.DUCK_WIN
            else:
                if not self.board.has_path_to_any_open_edge(self.board.duck_pos):
                    self.state = GameState.PLAYER_WIN
                else:
                    self.turn = Turn.PLAYER
            return None

        return (self.board.duck_pos, nxt)

    def finalize_duck_move(self, to_cell):
        self.board.set_duck(to_cell)

        if self.board.duck_on_edge(to_cell):
            self.state = GameState.DUCK_WIN
        elif not self.board.has_path_to_any_open_edge(self.board.duck_pos):
            self.state = GameState.PLAYER_WIN
        else:
            self.turn = Turn.PLAYER

    # ================= LEVEL CONTROL =================
    def restart_level(self):
        self.board = Board(self.level)
        self.duck_agent = DuckAgent(self.board)
        self.turn = Turn.PLAYER
        self.state = GameState.RUNNING

    def next_level(self):
        self.level += 1
        if self.level not in LEVELS:
            self.level = 1

        self.board = Board(self.level)
        self.duck_agent = DuckAgent(self.board)
        self.turn = Turn.PLAYER
        self.state = GameState.RUNNING
