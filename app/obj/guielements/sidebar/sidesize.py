import math
from typing import Any, Literal, Optional, cast

import pygame
import thorpy as tp
from Box2D import b2CircleShape, b2PolygonShape
from obj.guielements.numberinput import NumberInput


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
            self.angle1 = NumberInput("", placeholder="00.00")
            self.edge = NumberInput("", placeholder="00.00")
            self.angle2 = NumberInput("", placeholder="00.00")
            self.angle1.set_only_non_negative()
            self.edge.set_only_non_negative()
            self.angle2.set_only_non_negative()
            self.angle1.max_length = 5
            self.edge.max_length = 5
            self.angle2.max_length = 5
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
                self.radius = NumberInput("", placeholder="00.00")
                self.radius.set_only_non_negative()
                self.radius.max_length = 5
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
                self.w = NumberInput("", placeholder="00.00")
                self.h = NumberInput("", placeholder="00.00")
                self.w.set_only_non_negative()
                self.h.set_only_non_negative()
                self.w.max_length = 5
                self.h.max_length = 5
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
        if body is None or not hasattr(body, "fixtures") or not body.fixtures:
            return

        shape = body.fixtures[0].shape

        if self.shape_type == "circle" and isinstance(shape, b2CircleShape):
            radius: float = float(shape.radius)
            radius = positive_min(radius)

            if hasattr(self, "radius"):
                self.radius.value = f"{radius:.2f}"

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

        elif self.shape_type == "triangle" and isinstance(shape, b2PolygonShape):
            verts = list(shape.vertices)
            if len(verts) != 3:
                return

            def dist(a, b):
                return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

            edges = [(verts[0], verts[1]), (verts[1], verts[2]), (verts[2], verts[0])]
            base_edge = min(
                edges, key=lambda e: abs(e[0][1] - e[1][1])
            )  # najmniejsze Δy

            A, B = base_edge
            C = [v for v in verts if v not in base_edge][0]

            edge_val = dist(A, B)

            direction = 1.0 if B[0] > A[0] else -1.0

            a_len = dist(B, C)
            b_len = dist(A, C)
            c_len = edge_val

            def angle(opposite, s1, s2):
                num = s1**2 + s2**2 - opposite**2
                den = 2 * s1 * s2
                if den == 0:
                    return 0.0
                return math.degrees(math.acos(max(-1.0, min(1.0, num / den))))

            angle1_val = angle(a_len, b_len, c_len)  # przy A
            angle2_val = angle(b_len, a_len, c_len)  # przy B

            if hasattr(self, "edge"):
                self.edge.value = f"{edge_val:.2f}"
            if hasattr(self, "angle1"):
                self.angle1.value = f"{angle1_val:.2f}"
            if hasattr(self, "angle2"):
                self.angle2.value = f"{angle2_val:.2f}"
