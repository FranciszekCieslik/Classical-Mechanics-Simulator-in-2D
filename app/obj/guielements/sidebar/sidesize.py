from typing import Literal, Optional

import pygame
import thorpy as tp


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
        self.launcher = self.box.get_updater()

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
