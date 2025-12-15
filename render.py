import math
import sys
import pygame
from config import Config, Colors, clamp, make_sound
from board import Cell, TileType, MAX_LEVEL
from game import GameManager, GameState, Turn
from ui import Button

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


    def draw_popup(self):
        w,h = self.screen.get_size()
        overlay = pygame.Surface((w,h), pygame.SRCALPHA)
        overlay.fill((0,0,0,Colors.OVERLAY_ALPHA))
        self.screen.blit(overlay, (0,0))
        popup_w = min(680, w-60)
        popup_h = min(340, h-120)
        popup_x = (w - popup_w)//2
        popup_y = (h - popup_h)//2
        elapsed = 0
        if self.state_changed_at:
            elapsed = pygame.time.get_ticks() - self.state_changed_at
        t = clamp(elapsed / 350.0, 0.0, 1.0)
        scale = 0.7 + 0.3 * (math.sin(t * math.pi/2) ** 0.9)
        sw = int(popup_w * scale)
        sh = int(popup_h * scale)
        sx = (w - sw)//2
        sy = (h - sh)//2
        scaled_rect = pygame.Rect(sx, sy, sw, sh)
        pygame.draw.rect(self.screen, Colors.POPUP_BG, scaled_rect, border_radius=12)
        pygame.draw.rect(self.screen, Colors.BUTTON, scaled_rect, 3, border_radius=12)

        # Select message based on state and whether final level
        if self.gm.state == GameState.PLAYER_WIN:
            if self.gm.level >= MAX_LEVEL:
                msg = "Congrats! You have caught the duck!"
                sub = "Would you like to start again?"
            else:
                msg = "You win this level!"
                sub = "Let's see the next..."
            if not hasattr(self, "_played_win"):
                self.play_win()
                self._played_win = True
        else:
            msg = "The duck escaped!"
            sub = "Retry again."
            if not hasattr(self, "_played_lose"):
                self.play_lose()
                self._played_lose = True
                

        title = self.font_big.render(msg, True, Colors.TEXT)
        self.screen.blit(title, title.get_rect(center=(w//2, sy + sh//3)))
        subtitle = self.font_med.render(sub, True, Colors.TEXT)
        self.screen.blit(subtitle, subtitle.get_rect(center=(w//2, sy + sh//3 + 44)))
        
        if not self.popup_buttons:
            self.build_popup_buttons(w,h)
        mouse_pos = pygame.mouse.get_pos()
        for b in self.popup_buttons:
            b.update_hover(mouse_pos)
            b.draw(self.screen)

    def main_loop(self):
        while self.running:
            for event in pygame.event.get():

            #Quit 
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.running = False

            # Window Resize 
                elif event.type == pygame.VIDEORESIZE:
                    new_w = max(event.w, Config.WINDOW_MIN_W)
                    new_h = max(event.h, Config.WINDOW_MIN_H)
                    self.screen = pygame.display.set_mode(
                        (new_w, new_h), pygame.RESIZABLE
                )
                    self.popup_buttons = []

            #ESC 
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            # START MENU
                elif self.in_start_menu and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    start_rect, exit_rect = self.last_menu_rects
                    if start_rect.collidepoint(event.pos):
                        self._on_start()
                    elif exit_rect.collidepoint(event.pos):
                        self._on_exit()

            # GAME click
                elif not self.in_start_menu and self.gm.state == GameState.RUNNING:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.gm.turn == Turn.PLAYER:
                            self.handle_grid_click(event.pos)

            # POPUP BUTTONS
                if self.popup_buttons:
                    for b in self.popup_buttons:
                        b.handle_event(event)

        # Detect State Change
            if self.gm.state != self.prev_state:
                self.state_changed_at = pygame.time.get_ticks()
                self.popup_buttons = []
                self.popup_scale_done = False
                if hasattr(self, "_played_win"):
                    del self._played_win
                if hasattr(self, "_played_lose"):
                    del self._played_lose
                    
                self.prev_state = self.gm.state

        #START MENU
            if self.in_start_menu:
                self.last_menu_rects = self.draw_start_menu()
                pygame.display.update()
                self.clock.tick(Config.FPS)
                continue

        # GAME
            self.screen.fill((180, 220, 255))
            self.draw_grid()
            pygame.display.update()

        # Duck turn
            if self.gm.state == GameState.RUNNING and self.gm.turn == Turn.DUCK:
                mv = self.gm.duck_take_turn()
                if mv:
                    self.animate_duck(mv[0], mv[1])
                    self.gm.finalize_duck_move(mv[1])

        # Popup
            if self.gm.state in (GameState.PLAYER_WIN, GameState.DUCK_WIN):
                self.draw_popup()
                pygame.display.update()

            self.clock.tick(Config.FPS)

        pygame.quit()

