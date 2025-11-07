import pygame
import thorpy as tp


class SideBar:
    def __init__(self):
        self.screen: pygame.Surface = pygame.display.get_surface()
        self.visible: bool = False
        self.height: int = self.screen.get_height()
        self.top_margin: int = 60
        self.speed: int = 12

        # --- Thorpy Elements ---
        self.title = tp.Text("Object Controls", font_size=18)
        self.main_group = tp.Group(elements=[self.title], margins=(0, 0))
        self.box = tp.Box([self.main_group])
        self.box.set_topleft(self.screen.get_width(), self.top_margin)
        self.launcher = self.box.get_updater()

        self.width: int = self.box.get_rect().size[0]
        self.offset: int = self.width

    def toggle(self):
        self.visible = not self.visible

    def hide(self):
        self.visible = False

    def update(self):
        target_offset = 0 if self.visible else self.screen.get_width()
        if abs(self.offset - target_offset) > 1:
            self.offset += (target_offset - self.offset) / self.speed
        x = self.screen.get_width() - self.width + int(self.offset)
        self.box.set_topleft(x, self.top_margin)
        self.launcher.reaction(pygame.event.get())
        self.launcher.update()
