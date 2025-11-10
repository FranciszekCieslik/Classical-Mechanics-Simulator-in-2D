from typing import Optional, Union

import pygame
import thorpy as tp
from obj.guielements.sidebar.featurespanel import FeaturesPanel
from obj.guielements.sidebar.selectortype import SelectorType
from obj.guielements.sidebar.sidesize import SideSize
from obj.realobject import RealObject
from thorpy import loops

PanelType = Union["SideBar", SideSize, SelectorType, FeaturesPanel]


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
        # --- Size Bars ---
        self.size_rectangle = SideSize("rectangle")
        self.size_triangle = SideSize("triangle")
        self.size_circle = SideSize("circle")
        # --- SelectorType ---
        self.featurespanel = FeaturesPanel()

        def val_show_features():
            con = self.selectortype.checkboxpool.get_value()
            self.featurespanel.show(con)
            self.reset_width()
            self.update()

        self.selectortype = SelectorType(val_show_features)
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
        self.title_line = tp.Line('h', 360)
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
        self.box.set_topleft(self.screen.get_width() + self.width, self.top_margin)
        self.box.set_size((self.width, self.height))
        self.box.set_bck_color((0, 0, 0))

        self.rect: pygame.Rect = self.box.rect

        self.size_rectangle.rebuild(self.rect)
        self.size_triangle.rebuild(self.rect)
        self.size_circle.rebuild(self.rect)
        self.selectortype.rebuild(self.size_circle.box.rect)
        self.featurespanel.rebuild(self.selectortype.box.rect)

        self.container = tp.Group(
            [
                self.box,
                self.size_rectangle.box,
                self.size_triangle.box,
                self.size_circle.box,
                self.selectortype.box,
                self.featurespanel.box,
            ],
            mode=None,
        )

    def show(self) -> None:
        if self.visible:
            self.hide()
            self.update()
            return
        self.visible = True
        if not self.obj:
            return
        shape_type = self.obj.shape_type
        self.size_rectangle.show(shape_type)
        self.size_triangle.show(shape_type)
        self.size_circle.show(shape_type)
        self.selectortype.show()
        self.featurespanel.show(self.selectortype.checkboxpool.get_value())

    def hide(self) -> None:
        self.visible = False
        self.size_rectangle.hide()
        self.size_triangle.hide()
        self.size_circle.hide()
        self.selectortype.hide()
        self.featurespanel.hide()

    def update(self) -> None:
        target_offset = 0 if self.visible else self.screen.get_width()
        if abs(self.offset - target_offset) > 1:
            self.offset += int((target_offset - self.offset) / self.speed)
        else:
            self.offset = target_offset
        x = self.screen.get_width() - self.width + int(self.offset)
        self.box.set_topleft(x, self.top_margin)

        self.reset_width()

        panels: list[PanelType] = [
            self.size_rectangle,
            self.size_triangle,
            self.size_circle,
            self.selectortype,
            self.featurespanel,
        ]

        visible_panels = [p for p in panels if p.visible]

        x = self.box.rect.left
        events = pygame.event.get()
        for panel in panels:
            if panel in visible_panels:
                panel.offset = self.offset
                panel.box.set_topleft(x, panel.top_margin)
            else:
                panel.offset = self.screen.get_width()
                panel.box.set_topleft(
                    self.screen.get_width() + self.width, panel.top_margin
                )
        self.selectortype.checkboxpool.toggle()

    def get_data_from_real_obj(self, rlobjct: RealObject) -> None:
        self.obj = rlobjct
        self.text.set_value(self.obj.shape_type)
        body = self.obj.physics.body
        pos = body.position
        self.x_pos.value = str(round(pos.x, 3))
        self.y_pos.value = str(-round(pos.y, 3))
        self.rotation.value = str(round(body.angle, 3))
        self.selectortype.checkboxpool.set_value(
            'static' if self.obj.physics.is_static else 'dynamic'
        )
        if not self.obj.physics.is_static:
            self.featurespanel.set_data_from_obj(
                body, self.obj.start_linearVelocity, self.obj.start_angularVelocity
            )

    def reset_width(self) -> None:
        panels: list[PanelType] = [
            self,
            self.size_rectangle,
            self.size_triangle,
            self.size_circle,
            self.selectortype,
            self.featurespanel,
        ]

        boxes = [p.box for p in panels]
        max_width = max(box.rect.width for box in boxes)
        visible_offsets = [
            int(panel.offset)
            for panel in panels
            if panel.visible and panel.offset is not None
        ]
        min_offset = min(visible_offsets) if visible_offsets else int(self.offset or 0)
        for box in boxes:
            box.set_size((max_width, box.rect.height))

        for panel in panels:
            panel.width = max_width
            if panel.rect is not None:
                panel.rect.width = max_width

            if panel.visible:
                panel.offset = min_offset
