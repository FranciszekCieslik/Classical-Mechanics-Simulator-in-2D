from typing import Optional

import pygame
import thorpy as tp


class FeaturesPanel:
    def __init__(self) -> None:
        self.screen: pygame.Surface = pygame.display.get_surface()
        self.visible: bool = False
        self.speed: int = 12
        self.rect: Optional[pygame.Rect] = None
        self.width: Optional[int] = None
        self.offset: Optional[int] = None
        self.top_margin: Optional[int] = None
        elements = [tp.Text("FEATURES")]
        self.group = tp.Group(elements, mode="h")
        self.box = tp.Box([self.group])
        self.launcher = self.box.get_updater()

    def rebuild(self, rect: pygame.Rect) -> None:
        self.rect = rect
        self.width = rect.width
        self.offset = self.width
        self.top_margin = rect.bottom
        self.box.set_size((self.width, self.box.rect.height))
        self.box.set_topleft(self.rect.left, self.top_margin)

    def update(self, x: int) -> None:
        self.box.set_topleft(x, self.top_margin)
        self.launcher.reaction(pygame.event.get())
        self.launcher.update()

    def show(self, val: str) -> None:
        if isinstance(val, list):
            val = val[0] if val else ''
        self.visible = val != 'static'

    def hide(self) -> None:
        self.visible = False
