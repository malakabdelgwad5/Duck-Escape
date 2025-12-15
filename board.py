import random
from collections import deque
import heapq




Cell = tuple[int, int]

LEVELS = {
    1: {"rows": 10, "cols": 10, "density": 0.14},
    2: {"rows": 12, "cols": 12, "density": 0.17},
    3: {"rows": 15, "cols": 15, "density": 0.20},
}

MAX_LEVEL = max(LEVELS.keys())


class TileType:
    EMPTY = 0
    BLOCK = 1
    DUCK = 2
    PLAYER_BLOCK = 3


class Board:
    def __init__(self, level: int):
        if level not in LEVELS:
            level = 1

        self.level = level
        cfg = LEVELS[level]
        self.rows = cfg["rows"]
        self.cols = cfg["cols"]
        self.density = cfg["density"]
        self.grid = [[TileType.EMPTY]*self.cols for _ in range(self.rows)]
        self.duck_pos = (0, 0)
        self.reset_map()

    def in_bounds(self, cell: Cell):
        r, c = cell
        return 0 <= r < self.rows and 0 <= c < self.cols

    def get_neighbors(self, cell: Cell):
        r, c = cell
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nb = (r+dr, c+dc)
            if self.in_bounds(nb):
                yield nb

    def is_walkable(self, cell: Cell):
        r, c = cell
        return self.grid[r][c] not in (TileType.BLOCK, TileType.PLAYER_BLOCK)

    def reset_map(self):
        self.duck_pos = (random.randint(1, self.rows-2),
                         random.randint(1, self.cols-2))
        self._place_obstacles()

    def place_player_block(self, cell: Cell):
        r, c = cell
        if self.grid[r][c] == TileType.EMPTY:
            self.grid[r][c] = TileType.PLAYER_BLOCK
            return True
        return False

    def set_duck(self, cell: Cell):
        r, c = self.duck_pos
        self.grid[r][c] = TileType.EMPTY
        self.duck_pos = cell
        r, c = cell
        self.grid[r][c] = TileType.DUCK

    def duck_on_edge(self, cell=None):
        r, c = cell or self.duck_pos
        return r == 0 or c == 0 or r == self.rows-1 or c == self.cols-1

    def has_path_to_any_open_edge(self, start: Cell):
        q = deque([start])
        visited = {start}
        while q:
            cur = q.popleft()
            if self.duck_on_edge(cur):
                return True
            for nb in self.get_neighbors(cur):
                if nb not in visited and self.is_walkable(nb):
                    visited.add(nb)
                    q.append(nb)
        return False

    def _place_obstacles(self):
        total = int(self.rows * self.cols * self.density)
        placed = 0
        while placed < total:
            r = random.randrange(self.rows)
            c = random.randrange(self.cols)
            if (r,c) != self.duck_pos and self.grid[r][c] == TileType.EMPTY:
                self.grid[r][c] = TileType.BLOCK
                placed += 1
    def get_all_open_edges(self):
        edges = []

        
        for c in range(self.cols):
            if self.is_walkable((0, c)):
                edges.append((0, c))
            if self.is_walkable((self.rows - 1, c)):
                edges.append((self.rows - 1, c))

        
        for r in range(self.rows):
            if self.is_walkable((r, 0)):
                edges.append((r, 0))
            if self.is_walkable((r, self.cols - 1)):
                edges.append((r, self.cols - 1))

        
        return list(dict.fromkeys(edges))


# This algorithm show how Duck Playing  
# BY malak Abd elgwad
class DuckAgent:
    def __init__(self, board):
        self.board = board

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star(self, start, goal):
        open_heap = []
        heapq.heappush(open_heap, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        closed = set()

        while open_heap:
            _, current = heapq.heappop(open_heap)

            if current == goal:
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                return path[::-1]

            if current in closed:
                continue

            closed.add(current)

            for nb in self.board.get_neighbors(current):
                if nb != goal and not self.board.is_walkable(nb):
                    continue

                tentative = g_score[current] + 1
                if tentative < g_score.get(nb, 999999):
                    came_from[nb] = current
                    g_score[nb] = tentative
                    f_score[nb] = tentative + self.heuristic(nb, goal)
                    heapq.heappush(open_heap, (f_score[nb], nb))

        return None

    def next_step_towards_nearest_edge(self):
        start = self.board.duck_pos
        targets = self.board.get_all_open_edges()

        best_path = None
        best_len = None

        for t in targets:
            path = self.a_star(start, t)
            if path:
                if best_path is None or len(path) < best_len:
                    best_path = path
                    best_len = len(path)

        if not best_path or len(best_path) < 2:
            return None

        return best_path[1]
