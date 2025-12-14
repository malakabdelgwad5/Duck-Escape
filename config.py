import array
import pygame
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    FPS: int = 60
    UI_HEIGHT: int = 96
    MIN_TILE: int = 12
    START_TILE: int = 48
    DUCK_MOVE_MS: int = 90
    WINDOW_MIN_W: int = 480
    WINDOW_MIN_H: int = 360
    POPUP_AUTO_MS: int = 1200


def clamp(v, a, b):
    return max(a, min(b, v))


def make_sound(frequency=440, duration=0.08, volume=0.4):
    sample_rate = 44100
    n_samples = max(1, int(sample_rate * duration))
    buf = array.array("h")
    amplitude = int(32767 * volume)
    period = max(1, int(sample_rate / max(1, frequency)))
    half = period // 2

    for i in range(n_samples):
        buf.append(amplitude if (i % period) < half else -amplitude)

    try:
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None


class Colors:
    EMPTY = (50, 180, 50)
    BLOCK = (100, 100, 100)
    PLAYER_BLOCK = (200, 150, 50)
    DUCK = (255, 182, 193)
    GRID_LINE = (30, 30, 30)
    UI_BG = (22, 22, 22)
    BUTTON = (38, 38, 38)
    BUTTON_HOVER = (70, 70, 70)
    TEXT = (230, 230, 230)
    POPUP_BG = (14, 18, 40)
    OVERLAY_ALPHA = 160
