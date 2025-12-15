import pygame
from config import Colors


class Button:
    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font, onclick=None):
        self.rect = rect
        self.text = text
        self.font = font
        self.onclick = onclick
        self.hover = False

    def update_hover(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hover and self.onclick:
                self.onclick()

    def draw(self, surf):
        color = Colors.BUTTON_HOVER if self.hover else Colors.BUTTON
        pygame.draw.rect(surf, color, self.rect, border_radius=10)

        txt = self.font.render(self.text, True, Colors.TEXT)
        surf.blit(txt, txt.get_rect(center=self.rect.center))

