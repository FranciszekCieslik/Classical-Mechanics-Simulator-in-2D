from typing import Optional

import pygame
import thorpy as tp
from obj.guielements.sidesize import SideSize
from obj.realobject import RealObject


class SideBar:
    def __init__(self) -> None:
        self.screen: pygame.Surface = pygame.display.get_surface()
        self.visible: bool = False
        self.speed: int = 12
        self.obj: Optional[RealObject] = None
        self.top_margin: int = 60
        self.width: int = 300
        self.height: int = 165
        self.offset: int = self.width
        self.rect = pygame.Rect(
            self.screen.get_width() - self.width,
            self.top_margin,
            self.width,
            self.height,
        )

        # --- Size Bars ---
        self.size_rectangle = SideSize("rectangle", self.rect, self.top_margin)
        self.size_triangle = SideSize("triangle", self.rect, self.top_margin)
        self.size_circle = SideSize("circle", self.rect, self.top_margin)

        # --- Thorpy Elements ---
        ico_path = "app/assets/icons/x-square.svg"
        img = pygame.image.load(ico_path)
        img = pygame.transform.smoothscale(img, (30, 30))
        variant = tp.graphics.change_color_on_img(
            img, img.get_at((0, 0)), (100, 100, 100)
        )
        xbtn = tp.ImageButton("", img.copy(), img_hover=variant)
        xbtn.at_unclick = self.hide

        # --- Title ---
        self.title = tp.Text("Object Controls", font_size=18)
        self.title_line = tp.Line('h', self.title.get_current_width())
        titlegroup = tp.Group(
            elements=[xbtn, self.title], mode="h", margins=(0, 0), gap=15
        )

        # --- Position ---
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
        self.box.set_topleft(self.rect.left, self.rect.top)
        self.box.set_size((self.rect.width, self.rect.height))
        self.launcher = self.box.get_updater()

        self.rect = self.box.rect
        self.size_rectangle.on__init(self.rect, self.top_margin)
        self.size_triangle.on__init(self.rect, self.top_margin)
        self.size_circle.on__init(self.rect, self.top_margin)

    def show(self) -> None:
        if self.visible:
            self.hide()
            self.update()
            return
        self.visible = True
        if self.obj:
            shape_type = self.obj.shape_type
            self.size_rectangle.show(shape_type)
            self.size_triangle.show(shape_type)
            self.size_circle.show(shape_type)

    def hide(self) -> None:
        self.visible = False
        self.size_rectangle.hide()
        self.size_triangle.hide()
        self.size_circle.hide()

    def update(self) -> None:
        target_offset = 0 if self.visible else self.screen.get_width()
        if abs(self.offset - target_offset) > 1:
            self.offset += int((target_offset - self.offset) / self.speed)
        x = self.screen.get_width() - self.width + int(self.offset)
        self.box.set_topleft(x, self.top_margin)

        self.reset_width()

        self.size_rectangle.update()
        self.size_triangle.update()
        self.size_circle.update()

        self.launcher.reaction(pygame.event.get())
        self.launcher.update()

    def get_data_from_real_obj(self, rlobjct: RealObject) -> None:
        self.obj = rlobjct
        self.text.set_value(self.obj.shape_type)
        body = self.obj.physics.body
        pos = body.position
        self.x_pos.value = str(round(pos.x, 3))
        self.y_pos.value = str(-round(pos.y, 3))
        self.rotation.value = str(round(body.angle, 3))

    def reset_width(self) -> None:
        max_width = max(
            [
                self.box.rect.width,
                self.size_rectangle.box.rect.width,
                self.size_triangle.box.rect.width,
                self.size_circle.box.rect.width,
            ]
        )

        # Ustawienie wspólnej szerokości
        self.box.set_size((max_width, self.box.rect.height))
        self.size_rectangle.box.set_size(
            (max_width, self.size_rectangle.box.rect.height)
        )
        self.size_triangle.box.set_size((max_width, self.size_triangle.box.rect.height))
        self.size_circle.box.set_size((max_width, self.size_circle.box.rect.height))

        # Synchronizacja atrybutów
        self.width = max_width
        self.size_rectangle.width = max_width
        self.size_triangle.width = max_width
        self.size_circle.width = max_width
