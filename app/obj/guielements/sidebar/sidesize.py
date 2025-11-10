from typing import Any, Literal, Optional, cast

import pygame
import thorpy as tp
from Box2D import b2CircleShape, b2PolygonShape


def clamp_angle(value: float) -> float:
    return max(0.0, min(90.0, value))


def positive_min(value: float) -> float:
    return max(0.01, value)


class SideSize:
    def __init__(self, shape_type: Literal["triangle", "circle", "rectangle"]):
        self.shape_type = shape_type
        self.screen: pygame.Surface = pygame.display.get_surface()
        self.visible: bool = False
        self.speed: int = 12
        self.rect: Optional[pygame.Rect] = None
        self.width: Optional[int] = None
        self.offset: Optional[int] = self.width
        self.top_margin: Optional[int] = None

        if shape_type == "triangle":
            self.angle1 = tp.TextInput("", placeholder="0.00")
            self.edge = tp.TextInput("", placeholder="0.00")
            self.angle2 = tp.TextInput("", placeholder="0.00")
            self.angle1.set_only_numbers()
            self.edge.set_only_numbers()
            self.angle2.set_only_numbers()
            self.group1 = tp.Group(
                [
                    tp.Text("Angle 1:", font_size=14),
                    self.angle1,
                    tp.Text("Edge:", font_size=14),
                    self.edge,
                ],
                mode="h",
            )
            self.group2 = tp.Group(
                [tp.Text("Angle 2:", font_size=14), self.angle2], mode="h"
            )
            self.group = tp.Group([self.group1, self.group2])
        else:
            if shape_type == "circle":
                self.radius = tp.TextInput("", placeholder="0.00")
                self.radius.set_only_numbers()
                self.group1 = tp.Group(
                    [
                        tp.Text("Radius:", font_size=14),
                        self.radius,
                    ],
                    mode="h",
                )
                self.group2 = tp.Group([tp.Text("", font_size=14)])
                self.group = tp.Group([self.group1, self.group2])
            elif shape_type == "rectangle":
                self.w = tp.TextInput("", placeholder="0.00")
                self.h = tp.TextInput("", placeholder="0.00")
                self.w.set_only_numbers()
                self.h.set_only_numbers()
                elements = [
                    tp.Text("Width:", font_size=14),
                    self.w,
                    tp.Text("Height:", font_size=14),
                    self.h,
                ]
                self.group1 = tp.Group(elements, mode="h")
                self.group2 = tp.Group([tp.Text("", font_size=14)])
                self.group = tp.Group([self.group1, self.group2])
            else:
                elements = [tp.Text("Unsupported shape type")]
                self.group = tp.Group(elements, mode="h")
        self.box = tp.Box([self.group])
        self.box.set_bck_color((0, 0, 0))

    def rebuild(self, rect: pygame.Rect):
        self.rect = pygame.Rect(rect.left, rect.bottom, rect.width, rect.height)
        self.width = rect.width
        self.offset = self.width
        self.top_margin = rect.bottom
        self.box.set_topleft(self.rect.left, self.top_margin)
        self.box.set_size((self.width, self.box.rect.height))

    def show(self, shape_type: str) -> None:
        self.visible = self.shape_type == shape_type

    def hide(self):
        self.visible = False

    def set_size_from_obj(self, body: Any) -> None:
        """
        Pobiera rozmiary kształtu z obiektu pybox2d (staticbody/dynamicbody)
        i przystosowuje je do TextInput, uwzględniając:
        - angles w zakresie 0–90
        - wartości dodatnie z min. 0.01
        """
        if body is None or not hasattr(body, "fixtures") or not body.fixtures:
            return

        shape = body.fixtures[0].shape

        # -----------------------------------------
        # ✅ CIRCLE (b2CircleShape)
        # -----------------------------------------
        if self.shape_type == "circle" and isinstance(shape, b2CircleShape):
            radius: float = float(shape.radius)
            radius = positive_min(radius)

            if hasattr(self, "radius"):
                self.radius.value = f"{radius:.2f}"

        # -----------------------------------------
        # ✅ RECTANGLE (b2PolygonShape → 4 vertices)
        # -----------------------------------------
        elif self.shape_type == "rectangle" and isinstance(shape, b2PolygonShape):
            poly = cast(b2PolygonShape, shape)

            # Odczytujemy bounding box ze zbioru vertexów
            xs = [v[0] for v in poly.vertices]
            ys = [v[1] for v in poly.vertices]

            width = positive_min(abs(max(xs) - min(xs)))
            height = positive_min(abs(max(ys) - min(ys)))

            if hasattr(self, "w"):
                self.w.value = f"{width:.2f}"
            if hasattr(self, "h"):
                self.h.value = f"{height:.2f}"

        # -----------------------------------------
        # ✅ TRIANGLE (b2PolygonShape → 3 vertexy)
        # -----------------------------------------
        elif self.shape_type == "triangle" and isinstance(shape, b2PolygonShape):
            poly = cast(b2PolygonShape, shape)
            verts = poly.vertices

            if len(verts) == 3:
                # Długości krawędzi trójkąta
                import math

                def dist(a: Any, b: Any) -> float:
                    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

                a = dist(verts[0], verts[1])
                b = dist(verts[1], verts[2])
                c = dist(verts[2], verts[0])

                # Zakładając edge = jedna z krawędzi → weźmy największą
                edge_val = positive_min(max(a, b, c))

                # Oblicz kąty wewnętrzne trójkąta
                def angle(opposite: float, s1: float, s2: float) -> float:
                    # prawo cosinusów
                    import math

                    num = s1**2 + s2**2 - opposite**2
                    den = 2 * s1 * s2
                    if den == 0:
                        return 0.0
                    ang = math.degrees(math.acos(max(-1.0, min(1.0, num / den))))
                    return clamp_angle(ang)

                angle1_val = angle(a, b, c)
                angle2_val = angle(b, a, c)

                if hasattr(self, "edge"):
                    self.edge.value = f"{edge_val:.2f}"
                if hasattr(self, "angle1"):
                    self.angle1.value = f"{angle1_val:.2f}"
                if hasattr(self, "angle2"):
                    self.angle2.value = f"{angle2_val:.2f}"
