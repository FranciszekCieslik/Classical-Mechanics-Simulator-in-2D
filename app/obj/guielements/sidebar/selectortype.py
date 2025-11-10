from typing import Callable, Optional

import pygame
import thorpy as tp
from obj.guielements.checkboxpool import CheckboxPool


class SelectorType:
    def __init__(self, fun: Callable):
        self.screen: pygame.Surface = pygame.display.get_surface()
        self.visible: bool = False
        self.speed: int = 12
        self.rect: Optional[pygame.Rect] = None
        self.width: Optional[int] = None
        self.offset: Optional[int] = self.width
        self.top_margin: Optional[int] = None
        self.checkboxpool = CheckboxPool(['static', 'dynamic'], fun, "h")

        elements = [self.checkboxpool.get()]

        self.group = tp.Group(elements, mode="h")
        self.box = tp.Box([tp.Line("h", 360), self.group])
        self.box.set_bck_color((0, 0, 0))

    def rebuild(self, rect: pygame.Rect):
        self.rect = rect
        self.width = rect.width
        self.offset = self.width
        self.top_margin = rect.bottom
        self.box.set_size((self.width, self.box.rect.height))
        self.box.set_topleft(self.rect.left, self.top_margin)

    def show(self) -> None:
        self.visible = True

    def hide(self):
        self.visible = False
