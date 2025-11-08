import pygame
import thorpy as tp


class SelectorType:
    def __init__(self, rect: pygame.Rect):
        self.screen: pygame.Surface = pygame.display.get_surface()
        self.visible: bool = False
        self.speed: int = 12
        self.rect = rect
        self.width: int = rect.width
        self.offset: int = self.width
        self.top_margin = rect.bottom

        self.checkboxpool = tp.TogglablesPool(
            "", ['static', 'dynamic'], 'static', 'checkbox'
        )
        elements = [self.checkboxpool]

        self.group = tp.Group(elements, mode="h")
        self.box = tp.Box([self.group])
        self.launcher = self.box.get_updater()

    def on__init(self, rect: pygame.Rect):
        self.rect = rect
        self.width = rect.width
        self.offset = self.width
        self.top_margin = rect.bottom
        self.box.set_size((self.width, self.box.rect.height))
        self.box.set_topleft(self.rect.left, self.top_margin)

    def update(self, x: int):
        self.box.set_topleft(x, self.top_margin)
        self.launcher.reaction(pygame.event.get())
        self.launcher.update()

    def show(self) -> None:
        self.visible = True

    def hide(self):
        self.visible = False
