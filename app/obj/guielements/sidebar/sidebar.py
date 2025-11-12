from typing import Optional, Union

import pygame
import thorpy as tp
from obj.guielements.sidebar.featurespanel import FeaturesPanel, allow_negative_input
from obj.guielements.sidebar.selectortype import SelectorType
from obj.guielements.sidebar.sidesize import SideSize
from obj.objectsmanager import ObjectsManager
from obj.physicobject import Features
from obj.realobject import RealObject

PanelType = Union["SideBar", SideSize, SelectorType, FeaturesPanel]

import math
from typing import Any, List, Tuple

from Box2D import b2PolygonShape


def triangle_from_angles(
    edge: float, angle1: float, angle2: float, body: Any
) -> list[tuple[float, float]]:
    # --- Bezpieczne wejście ---
    if body is None or not hasattr(body, "fixtures") or not body.fixtures:
        raise ValueError("Niepoprawny obiekt Box2D (body).")

    shape = body.fixtures[0].shape
    if not isinstance(shape, b2PolygonShape) or len(shape.vertices) != 3:
        raise ValueError("Oczekiwano trójkąta (b2PolygonShape z 3 wierzchołkami).")

    # --- Kierunek rysowania ---
    direction = 1.0 if edge >= 0 else -1.0
    edge = abs(edge)

    # --- Przeliczenie kątów na radiany ---
    A = math.radians(angle1)
    B = math.radians(angle2)
    C = math.radians(180 - (angle1 + angle2))

    # --- Długości pozostałych boków (prawo sinusów) ---
    a = edge * math.sin(A) / math.sin(C)
    b = edge * math.sin(B) / math.sin(C)

    # --- Wierzchołki lokalne (bazowy układ odniesienia) ---
    xC = b * math.cos(A)
    yC = b * math.sin(A)
    verts = [(0.0, 0.0), (edge, 0.0), (xC, yC)]

    # --- Odwrócenie, jeśli użytkownik rysował od prawej do lewej ---
    if direction < 0:
        verts = [(-x, y) for (x, y) in verts]

    # --- Centrowanie (Box2D wymaga centroidu w (0,0)) ---
    cx = sum(v[0] for v in verts) / 3.0
    cy = sum(v[1] for v in verts) / 3.0
    verts = [(x - cx, y - cy) for (x, y) in verts]

    old_verts = list(shape.vertices)

    # znajdź krawędź bazową w starym obiekcie (najbardziej pozioma)
    edges = [
        (old_verts[0], old_verts[1]),
        (old_verts[1], old_verts[2]),
        (old_verts[2], old_verts[0]),
    ]
    base_edge = min(edges, key=lambda e: abs(e[0][1] - e[1][1]))
    (A_old, B_old) = base_edge

    # wektor bazowy starego trójkąta
    dx, dy = (B_old[0] - A_old[0], B_old[1] - A_old[1])
    base_angle = math.atan2(dy, dx)  # orientacja w radianach

    # rotacja nowego trójkąta o tę samą orientację
    cos_a, sin_a = math.cos(base_angle), math.sin(base_angle)
    rotated_verts = [(x * cos_a - y * sin_a, x * sin_a + y * cos_a) for (x, y) in verts]

    cx_old = sum(v[0] for v in old_verts) / 3.0
    cy_old = sum(v[1] for v in old_verts) / 3.0
    rotated_verts = [(x - cx_old, y - cy_old) for (x, y) in rotated_verts]

    return rotated_verts


def safe_float(value, default=0.0) -> float:
    try:
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)
        value_str = str(value).strip()
        return float(value_str) if value_str else default
    except (ValueError, TypeError):
        return default


class SideBar:
    def __init__(self, objectmanager: ObjectsManager) -> None:
        self.objectmanager = objectmanager
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
        # --- Build Btn ---
        ico_path = "app/assets/icons/build.svg"
        img = pygame.image.load(ico_path)
        img = pygame.transform.smoothscale(img, (30, 30))
        variant = tp.graphics.change_color_on_img(
            img, img.get_at((0, 0)), (100, 100, 100)
        )
        build_btn = tp.ImageButton("", img.copy(), img_hover=variant)
        build_btn.at_unclick = self.apply
        helper = tp.Helper("Apply\nchanges", build_btn, countdown=30, offset=(80, 0))
        helper.set_font_size(12)
        # --- Title ---
        self.title = tp.Text("Object Controls", font_size=18)
        self.title_line = tp.Line('h', 360)
        titlegroup = tp.Group(
            elements=[xbtn, self.title, build_btn], mode="h", margins=(0, 0), gap=15
        )

        # --- Position ---
        self.text = tp.Text("", font_size=14)
        self.x_pos = tp.TextInput("", placeholder="00.000")
        allow_negative_input(self.x_pos)
        self.y_pos = tp.TextInput("", placeholder="00.000")
        allow_negative_input(self.y_pos)
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
        allow_negative_input(self.rotation)
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
        self.obj = None
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
        correct_y = -round(pos.y, 3) if pos.y != 0 else 0.00
        self.x_pos.value = str(round(pos.x, 3))
        self.y_pos.value = str(correct_y)
        self.rotation.value = str(round(math.degrees(body.angle) % 360, 3))

        if self.obj.shape_type == "circle":
            self.size_circle.set_size_from_obj(body)
        elif self.obj.shape_type == "triangle":
            self.size_triangle.set_size_from_obj(body)
        elif self.obj.shape_type == "rectangle":
            self.size_rectangle.set_size_from_obj(body)

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

    def apply_to_real_obj(self, rlobjct: RealObject) -> Optional[RealObject]:

        if self.obj is None:
            return None

        world = rlobjct.physics.world
        surface = rlobjct.visual.surface
        camera = rlobjct.visual.camera
        obj_type = self.selectortype.checkboxpool.get_value()
        shape_type = self.obj.shape_type
        position = (safe_float(self.x_pos.value), -1 * safe_float(self.y_pos.value))

        # --- rozmiar obiektu ---
        size: Optional[Union[float, tuple[float, float], list[tuple[float, float]]]] = (
            None
        )
        if shape_type == "circle":
            size = abs(safe_float(self.size_circle.radius.get_value()))
            if size == 0:
                self.size_circle.set_size_from_obj(self.obj.physics.body)
                size = abs(safe_float(self.size_circle.radius.get_value()))

        elif shape_type == "triangle":
            edge = abs(safe_float(self.size_triangle.edge.value))
            angle1 = abs(safe_float(self.size_triangle.angle1.value))
            angle2 = abs(safe_float(self.size_triangle.angle2.value))
            if 0 in [edge, angle1, angle2]:
                self.size_triangle.set_size_from_obj(self.obj.physics.body)
                edge = abs(safe_float(self.size_triangle.edge.value))
                angle1 = abs(safe_float(self.size_triangle.angle1.value))
                angle2 = abs(safe_float(self.size_triangle.angle2.value))
            size = triangle_from_angles(edge, angle1, angle2, self.obj.physics.body)

        elif shape_type == "rectangle":
            rec = self.size_rectangle
            w, h = abs(safe_float(rec.w.get_value())), abs(
                safe_float(rec.h.get_value())
            )
            if 0 in [w, h]:
                self.size_rectangle.set_size_from_obj(self.obj.physics.body)
                w, h = abs(safe_float(rec.w.get_value())), abs(
                    safe_float(rec.h.get_value())
                )
            size = (w, h)

        if size is None:
            return None

        angle = math.radians(safe_float(self.rotation.value))
        color = rlobjct.visual.color
        cell_size = rlobjct.cell_size

        # --- cechy fizyczne ---
        features = None
        if obj_type == 'dynamic':
            start_linearVelocity = (
                safe_float(self.featurespanel.start_velocity_x.value),
                -1 * safe_float(self.featurespanel.start_velocity_y.value),
            )
            start_angularVelocity = safe_float(
                self.featurespanel.start_angular_velocity.value
            )

            lv = (
                safe_float(self.featurespanel.curr_velocity_x.value),
                -1 * safe_float(self.featurespanel.curr_velocity_y.value),
            )
            av = safe_float(self.featurespanel.curr_angular_velocity.value)
            mass = safe_float(self.featurespanel.mass.value, 0.0)
            d = safe_float(self.featurespanel.density.value, 1.0)
            f = safe_float(self.featurespanel.friction.value, 0.5)
            r = safe_float(self.featurespanel.restitution.value, 0.0)

            features = Features(
                linearVelocity=lv,
                angularVelocity=av,
                density=d,
                friction=f,
                restitution=r,
            )

        new_obj = RealObject(
            world,
            surface,
            camera,
            obj_type,
            shape_type,
            size,
            position,
            angle,
            color,
            cell_size,
            features,
        )

        if obj_type == 'dynamic':
            if mass != 0:
                new_obj.physics.body.fixtures[0].density = (
                    new_obj.physics.body.fixtures[0].density
                    * (mass / new_obj.physics.body.mass)
                )
                new_obj.physics.body.mass = mass
                new_obj.physics.body.ResetMassData()
            new_obj.start_angle = rlobjct.start_angle
            new_obj.start_linearVelocity = start_linearVelocity
            new_obj.start_angularVelocity = start_angularVelocity
            if self.featurespanel.show_trajectory.value:
                if new_obj.trayectory:
                    new_obj.trayectory.visible = True

        return new_obj

    def apply(self):
        if self.obj:
            new_obj = self.apply_to_real_obj(self.obj)
            if new_obj:
                for i, old_obj in enumerate(self.objectmanager.objects):
                    if old_obj == self.obj:
                        self.objectmanager.objects[i] = new_obj
                        break
        self.hide()
