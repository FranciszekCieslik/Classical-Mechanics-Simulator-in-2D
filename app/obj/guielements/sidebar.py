from typing import Optional

import pygame
import thorpy as tp
from obj.realobject import RealObject


class SideBar:
    def __init__(self):
        self.screen: pygame.Surface = pygame.display.get_surface()
        self.visible: bool = False
        self.height: int = self.screen.get_height()
        self.top_margin: int = 60
        self.speed: int = 12
        self.obj: Optional[RealObject] = None

        # --- Thorpy Elements ---
        # exit btn
        ico_path = "app/assets/icons/x-square.svg"
        img = pygame.image.load(ico_path)
        img = pygame.transform.smoothscale(img, (30, 30))
        variant = tp.graphics.change_color_on_img(
            img, img.get_at((0, 0)), (100, 100, 100)
        )
        xbtn = tp.ImageButton("", img.copy(), img_hover=variant)
        xbtn.at_unclick = self.toggle

        # title
        self.title = tp.Text("Object Controls", font_size=18)
        self.title_line = tp.Line('h', self.title.get_current_width())
        titlegroup = tp.Group(
            elements=[xbtn, self.title], mode="h", margins=(0, 0), gap=15
        )

        # --- position ---
        self.text = tp.Text("", font_size=14)
        self.x_pos = tp.TextInput("", placeholder="00.000")
        self.x_pos.set_only_numbers()
        self.y_pos = tp.TextInput("", placeholder="00.000")
        self.y_pos.set_only_numbers()
        self.pos_group = tp.Group(
            [
                tp.Text("X:", font_size=14),
                self.x_pos,
                tp.Text("Y:", font_size=14),
                self.y_pos,
            ],
            "h",
        )

        # --- rotation ---
        self.rotation = tp.TextInput("", placeholder="00.000")
        self.rot_group = tp.Group(
            [
                tp.Text("Rotation", font_size=14),
                self.rotation,
                tp.Text("degree", font_size=14),
            ],
            "h",
        )

        # --- size ---

        # --- Static/Dynamic ---
        # --- main group ---
        self.main_group = tp.Group(
            elements=[
                titlegroup,
                self.title_line,
                self.text,
                self.pos_group,
                self.rot_group,
            ],
            margins=(0, 0),
        )
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

    def get_data_from_real_obj(self, rlobjct: RealObject):
        self.obj = rlobjct
        self.text.set_value(self.obj.shape_type)
        body = self.obj.physics.body
        pos = body.position
        self.x_pos.value = str(round(pos.x, 3))
        self.y_pos.value = str(-round(pos.y, 3))
        self.rotation.value = str(body.angle)
