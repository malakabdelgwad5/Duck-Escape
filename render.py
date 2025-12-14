import math
import sys
import pygame
from config import Config, Colors, clamp, make_sound
from board import Cell, TileType, MAX_LEVEL
from game import GameManager, GameState, Turn
from ui import Button


def ease_in_out(t):
    return t * t * (3 - 2 * t)

class Renderer:
    def __init__(self, gm:GameManager):
        pygame.init()
        try:
            pygame.mixer.pre_init(44100, -16, 1, 512)
            pygame.mixer.init()
            try:
                pygame.mixer.music.load("assets/mazeka.mp3")
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)  # لوب
            except:
                pass
        except Exception:
            pass
        self.gm = gm
        start_w = max(gm.board.cols * Config.START_TILE, Config.WINDOW_MIN_W)
        start_h = max(gm.board.rows * Config.START_TILE + Config.UI_HEIGHT, Config.WINDOW_MIN_H)
        
        start_w = max(1100, start_w)
        start_h = max(650, start_h)
        self.screen = pygame.display.set_mode(
            (start_w, start_h), pygame.RESIZABLE
            )   
        pygame.display.set_caption("Duck Escape")
        self.clock = pygame.time.Clock()
        self.running = True

        # fonts
        self.font_small = pygame.font.SysFont(None, 18)
        self.font_med = pygame.font.SysFont(None, 28)
        self.font_big = pygame.font.SysFont(None, 48)

        # load images fallback (use duck.jpg by default)
        self.duck_img = self._safe_load("assets/duck.png")
        self.goal_img = self._safe_load("goal.png")  # not used often but kept
        self.grass_img = self._safe_load("assets/grass (1).png")
        self.wall_img  = self._safe_load("assets/blockstone.png")
        # sounds
        self.place_sound = make_sound(100, 0.05, 0.4)
        self.click_sound = make_sound(1200, 0.05, 0.35)
        self.win_sound = make_sound(900, 0.18, 0.5)
        try:
            self.lose_sound = pygame.mixer.Sound("assets/duck_laugh.mp3")
            self.lose_sound.set_volume(0.7)
        except:
            self.lose_sound = None
        
        # UI
        self.tile = Config.START_TILE
        self.grid_pixels = (gm.board.cols * self.tile, gm.board.rows * self.tile)
        self.popup_buttons = []
        self.in_start_menu = True
        self.state_changed_at = None
        self.prev_state = gm.state  # for detecting state change
        # Build main menu buttons
        self._build_main_menu_buttons()

    def _build_main_menu_buttons(self):
        w,h = self.screen.get_size()
        bw, bh, gap = 220, 72, 24
        total_w = bw * 2 + gap
        start_x = (w - total_w)//2
        y = h//2 - bh//2
        self.main_buttons = [
            Button(pygame.Rect(start_x, y, bw, bh), "Start Game", self.font_med, onclick=self._on_start),
            Button(pygame.Rect(start_x + bw + gap, y, bw, bh), "Exit Game", self.font_med, onclick=self._on_exit),
        ]

    def _on_start(self):
        self.play_click()


        self.gm = GameManager(1)
        self.in_start_menu = False
        self.popup_buttons = []
        self.state_changed_at = None
        self.prev_state = self.gm.state


    def _on_exit(self):
        pygame.mixer.music.stop()
        self.play_click()
        pygame.quit()
        sys.exit()
        
        if event.type == pygame.QUIT:
            pygame.mixer.music.stop()
            self.running = False

    def _safe_load(self, fname):
      try:
        img = pygame.image.load(fname).convert()
        img.set_colorkey((0, 0, 0))  
        return img.convert_alpha()
      except Exception:
        return None


    def compute_tile(self):
        w,h = self.screen.get_size()
        grid_h_avail = max(16, h - Config.UI_HEIGHT)
        tile_w = w // self.gm.board.cols
        tile_h = grid_h_avail // self.gm.board.rows
        tile = max(Config.MIN_TILE, min(tile_w, tile_h))
        return tile, w, h, grid_h_avail

    def draw_start_menu(self):
    

        w, h = self.screen.get_size()

        # ---------- Gradient Background ----------
        for x in range(w):
            ratio = x / w
            r = int(206 * (1 - ratio) + 155 * ratio)
            g = int(255 * (1 - ratio) + 195 * ratio)
            b = int(224 * (1 - ratio) + 255 * ratio)
            pygame.draw.line(self.screen, (r, g, b), (x, 0), (x, h))

    # ---------- Fonts ----------
        title_font = pygame.font.SysFont("comic sans ms", 80, bold=True)
        btn_font   = pygame.font.SysFont("comic sans ms", 60, bold=True)
        small_font = pygame.font.SysFont("arial", 32)

    # ---------- Title (Stroke Effect) ----------
        title_text = "Duck Escape"
        for dx, dy in [(-3,0),(3,0),(0,-3),(0,3)]:
            stroke = title_font.render(title_text, True, (0, 90, 200))
            rect = stroke.get_rect(topleft=(80+dx, 60+dy))
            self.screen.blit(stroke, rect)

        title = title_font.render(title_text, True, (255, 200, 80))
        self.screen.blit(title, (80, 60))

    # ---------- Duck Image ----------
        duck_img = pygame.image.load("assets/duck.png").convert_alpha()
        duck_img = pygame.transform.smoothscale(duck_img, (220, 220))
        self.screen.blit(duck_img, (120, 220))

    # ---------- Buttons ----------
        start_text = btn_font.render("START GAME", True, (0, 0, 0))
        exit_text  = btn_font.render("EXIT GAME", True, (255, 80, 80))

        start_rect = start_text.get_rect(center=(w-350, 260))
        exit_rect  = exit_text.get_rect(center=(w-350, 360))

        self.screen.blit(start_text, start_rect)
        self.screen.blit(exit_text, exit_rect)

    # ---------- Bottom Hint ----------
        hint = small_font.render("Press start to play ...", True, (0, 0, 0))
        self.screen.blit(hint, hint.get_rect(center=(w//2, h-50)))

        return start_rect, exit_rect

        ## by giovanni