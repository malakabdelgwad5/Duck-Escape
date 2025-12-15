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
            pygame.init()
            pygame.mixer.init()
            pygame.mixer.set_num_channels(8)
            


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
        #duck
        self.win_img = self._safe_load("assets/sad_duck.png")
        self.lose_img = self._safe_load("assets/happy_duck.png")
        # sounds
        self.place_sound = make_sound(100, 0.05, 0.4)
        self.click_sound = make_sound(1200, 0.05, 0.35)
        self.win_sound = pygame.mixer.Sound("assets/duck_catch.mp3")


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
        self.gm.turn = Turn.PLAYER
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

            
    def play_place(self):
        try:
            if self.place_sound: self.place_sound.play()
        except Exception:
            pass
    def play_click(self):
        try:
            if self.click_sound: self.click_sound.play()
        except Exception:
            pass
    def play_win(self):
        try:
            if self.win_sound: self.win_sound.play()
        except Exception:
            pass
    def play_lose(self):
        try:
            if self.lose_sound: self.lose_sound.play()
        except Exception:
            pass

    def draw_grid(self):
        tile, w, h, grid_h_avail = self.compute_tile()
        self.tile = tile
        grid_w_px = self.gm.board.cols * tile
        grid_h_px = self.gm.board.rows * tile
        self.grid_pixels = (grid_w_px, grid_h_px)
        for r in range(self.gm.board.rows):
            for c in range(self.gm.board.cols):
                tile, w, h, grid_h_avail = self.compute_tile()
                self.tile = tile

                grid_w_px = self.gm.board.cols * tile
                grid_h_px = self.gm.board.rows * tile
                self.grid_pixels = (grid_w_px, grid_h_px)

                offset_x = (w - grid_w_px) // 2
                offset_y = 0
                x = offset_x + c * tile
                y = offset_y + r * tile
                rect = pygame.Rect(x, y, tile, tile)

                rect = pygame.Rect(x,y,tile,tile)
                if (r,c) == self.gm.board.duck_pos:
                    pygame.draw.rect(self.screen, (170, 220, 255), rect)  # سماوي
                else:
                    cell = self.gm.board.grid[r][c]
                    if cell == TileType.EMPTY and self.grass_img:
                        img = pygame.transform.smoothscale(self.grass_img, (tile, tile))
                        self.screen.blit(img, rect)
                    elif cell == TileType.BLOCK and self.wall_img:
                        img = pygame.transform.smoothscale(self.wall_img, (tile, tile))
                        self.screen.blit(img, rect)
                    elif cell == TileType.PLAYER_BLOCK and self.wall_img:
                        img = pygame.transform.smoothscale(self.wall_img, (tile, tile))
                        self.screen.blit(img, rect)
                    else:   
                        color = {
                            TileType.EMPTY: Colors.EMPTY,
                            TileType.BLOCK: Colors.BLOCK,
                             TileType.PLAYER_BLOCK: Colors.PLAYER_BLOCK
                                }[cell]
                        pygame.draw.rect(self.screen, color, rect)
                        pygame.draw.rect(self.screen, Colors.GRID_LINE, rect, 1)

        dr,dc = self.gm.board.duck_pos
        duck_center = (
            offset_x + dc * tile + tile // 2,
                offset_y + dr * tile + tile // 2
                )

        if self.duck_img:
            duck_s = pygame.transform.smoothscale(self.duck_img, (tile, tile))
            self.screen.blit(duck_s, duck_s.get_rect(center=duck_center))
        else:
            pygame.draw.circle(self.screen, Colors.DUCK, duck_center, max(4, tile//3))
        ui_y = offset_y + grid_h_px
        pygame.draw.rect(self.screen, Colors.UI_BG, pygame.Rect(0, ui_y, w, h - ui_y))
        text1 = self.font_small.render(f"Level {self.gm.level}    Turn: {'PLAYER' if self.gm.turn==Turn.PLAYER else 'DUCK'}", True, Colors.TEXT)
        self.screen.blit(text1, (10, ui_y + 8))
        text2 = self.font_small.render("Click empty tile to place block. ESC to quit.", True, Colors.TEXT)
        self.screen.blit(text2, (10, ui_y + 30))

    def handle_grid_click(self, pos):
        x, y = pos
        grid_w_px, grid_h_px = self.grid_pixels
        w, h = self.screen.get_size()

        offset_x = (w - grid_w_px) // 2
        offset_y = 0

    # translate mouse to grid space
        x -= offset_x
        y -= offset_y

        if not (0 <= x < grid_w_px and 0 <= y < grid_h_px):
            return

        c = x // self.tile
        r = y // self.tile

        if not self.gm.board.in_bounds((r, c)):
            return

        if self.gm.player_place((r, c)):
            self.play_place()

## by nada 
    def animate_duck(self, start:Cell, end:Cell):
        tile, w, h, _ = self.compute_tile()
        grid_w_px = self.gm.board.cols * tile

        offset_x = (w - grid_w_px) // 2
        offset_y = 0

        sx = offset_x + start[1]*tile + tile//2
        sy = offset_y + start[0]*tile + tile//2
        ex = offset_x + end[1]*tile + tile//2
        ey = offset_y + end[0]*tile + tile//2

        t0 = pygame.time.get_ticks()
        dur = max(120, Config.DUCK_MOVE_MS * 1.6) 

        while True:
            now = pygame.time.get_ticks()
            raw_t = (now - t0) / dur
            if raw_t >= 1:
                raw_t = 1.0
            t = ease_in_out(raw_t)
            
            cx = int(sx + (ex - sx) * t)
            cy = int(sy + (ey - sy) * t)

            # Bobbing effect
            bob = math.sin(t * math.pi) * (tile * 0.12)
            cy -= bob

            self.screen.fill((180, 220, 255))
            self.draw_grid()

            if self.duck_img:
                duck_s = pygame.transform.smoothscale(
                self.duck_img,
                (int(tile * 1.05), int(tile * 1.05))  
            )
                self.screen.blit(
                duck_s,
                duck_s.get_rect(center=(int(cx), int(cy)))
                )
            else:
                pygame.draw.circle(
                self.screen,
                Colors.DUCK,
                (int(cx), int(cy)),
                max(4, tile//3)
            )

            pygame.display.update()
            if t >= 1:
                break
            self.clock.tick(Config.FPS)

    def stop_all_sounds(self):

            try:
                if self.win_sound:
                    self.win_sound.stop()
            except:
                pass

            try:
                if self.lose_sound:
                    self.lose_sound.stop()
            except:
                pass
##########
    def draw_fullscreen_result(self):
        w, h = self.screen.get_size()
        self.screen.fill((200, 230, 255))

        mid_x = w // 2
        center_y = h // 2

  
        img_w = int(w * 0.28)
        img_h = int(h * 0.45)

        title_font = pygame.font.SysFont(None, 36)
        btn_y = center_y + img_h // 2 + 40

    # ================= PLAYER WIN =================
        if self.gm.state == GameState.PLAYER_WIN:

            if self.win_img:
                img = pygame.transform.smoothscale(self.win_img, (img_w, img_h))
                self.screen.blit(
                    img,
                    img.get_rect(center=(mid_x, center_y))
                )

            title = title_font.render("YOU WIN!", True, (0, 120, 0))
            self.screen.blit(
                title,
                title.get_rect(center=(mid_x, center_y - img_h // 2 - 30))
            )

            btn_rect = pygame.Rect(mid_x - 120, btn_y, 240, 60)

            def on_next():
                self.stop_all_sounds()
                self.play_click()
                self.gm.next_level()
                self.prev_state = self.gm.state
                if hasattr(self, "next_btn"):
                    del self.next_btn
                if hasattr(self, "_played_win"):
                    del self._played_win
                if hasattr(self, "_played_lose"):
                    del self._played_lose
            self.next_btn = Button(btn_rect, "Next Level", self.font_med, onclick=on_next)
            self.next_btn.update_hover(pygame.mouse.get_pos())
            self.next_btn.draw(self.screen)

    # ================= DUCK WIN =================
        elif self.gm.state == GameState.DUCK_WIN:


            if self.lose_img:
                img = pygame.transform.smoothscale(self.lose_img, (img_w, img_h))
                self.screen.blit(
                    img,
                    img.get_rect(center=(mid_x, center_y))
                )

            title = title_font.render("DUCK ESCAPED", True, (180, 0, 0))
            self.screen.blit(
                title,
                title.get_rect(center=(mid_x, center_y - img_h // 2 - 30))
            )

            btn_rect = pygame.Rect(mid_x - 120, btn_y, 240, 60)

            def on_retry():
                self.stop_all_sounds()
                self.play_click()
                self.gm.restart_level()
                self.prev_state = self.gm.state
                self.gm.state
                if hasattr(self, "retry_btn"):
                        del self.retry_btn
            
                if hasattr(self, "_played_win"):
                    del self._played_win
                if hasattr(self, "_played_lose"):
                    del self._played_lose
                    
            self.retry_btn = Button(btn_rect, "Try Again", self.font_med, onclick=on_retry)
            self.retry_btn.update_hover(pygame.mouse.get_pos())
            self.retry_btn.draw(self.screen)


        if self.gm.state == GameState.PLAYER_WIN:
            if not hasattr(self, "_played_win"):
                self.play_win()
                self._played_win = True
        elif self.gm.state == GameState.DUCK_WIN:
            if not hasattr(self, "_played_lose"):
                self.play_lose()
                self._played_lose = True


###########

    def main_loop(self):
        while self.running:
            # ================= EVENTS =================
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

                elif event.type == pygame.VIDEORESIZE:
                    w = max(event.w, Config.WINDOW_MIN_W)
                    h = max(event.h, Config.WINDOW_MIN_H)
                    self.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
                    self.popup_buttons.clear()

            # ---------- START MENU ----------
                if self.in_start_menu:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        start_rect, exit_rect = self.last_menu_rects
                        if start_rect.collidepoint(event.pos):
                            self._on_start()
                        elif exit_rect.collidepoint(event.pos):
                            self._on_exit()
                    continue

            # ---------- GAME INPUT ----------
                if (
                    self.gm.state == GameState.RUNNING
                    and self.gm.turn == Turn.PLAYER
                    and event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                ):
                    self.handle_grid_click(event.pos)

            # ---------- POPUP / RESULT BUTTONS ----------
                if self.popup_buttons:
                    for b in self.popup_buttons:
                        b.handle_event(event)
                # ---------- FULLSCREEN RESULT BUTTONS ----------
                if hasattr(self, "next_btn"):
                    self.next_btn.handle_event(event)

                if hasattr(self, "retry_btn"):
                    self.retry_btn.handle_event(event)

        # ================= GAME LOGIC =================

        # Duck turn (once)
            if (
                self.gm.state == GameState.RUNNING
                and self.gm.turn == Turn.DUCK
                and not self.gm.duck_moved
            ):
                mv = self.gm.duck_take_turn()
                if mv:
                    self.animate_duck(mv[0], mv[1])
                    self.gm.finalize_duck_move(mv[1])
                self.gm.duck_moved = True

        # ================= RENDER =================

            if self.in_start_menu:
                self.last_menu_rects = self.draw_start_menu()

            elif self.gm.state == GameState.RUNNING:
                self.screen.fill((180, 220, 255))
                self.draw_grid()

            else:  # PLAYER_WIN or DUCK_WIN
                self.draw_fullscreen_result()

            pygame.display.update()
            self.clock.tick(Config.FPS)

        pygame.quit()

#tasneem