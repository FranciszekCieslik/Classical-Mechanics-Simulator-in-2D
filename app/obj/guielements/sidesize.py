from typing import Literal

import pygame
import thorpy as tp


class SideSize:
    def __init__(
        self,
        shape_type: Literal["triangle", "circle", "rectangle"],
        rect: pygame.Rect,
        top_margin: int,
    ):
        self.screen: pygame.Surface = pygame.display.get_surface()
        self.visible: bool = False
        self.shape_type = shape_type
        self.speed: int = 12
        self.rect = rect
        self.width: int = rect.size[0]
        self.offset: int = self.width
        self.top_margin = rect.size[1] + top_margin

        if shape_type == "triangle":
            self.angle1 = tp.TextInput("", placeholder="0.00")
            self.edge = tp.TextInput("", placeholder="0.00")
            self.angle2 = tp.TextInput("", placeholder="0.00")
            self.group1 = tp.Group(
                [tp.Text("Angle 1:"), self.angle1, tp.Text("Edge:"), self.edge],
                mode="h",
            )
            self.group2 = tp.Group([tp.Text("Angle 2:"), self.angle2], mode="h")
            self.group = tp.Group([self.group1, self.group2])
        else:
            if shape_type == "circle":
                self.radius = tp.TextInput("", placeholder="0.00")
                elements = [
                    tp.Text("Radius:"),
                    self.radius,
                ]
                self.group = tp.Group(elements, mode="h")
            elif shape_type == "rectangle":
                self.w = tp.TextInput("", placeholder="0.00")
                self.h = tp.TextInput("", placeholder="0.00")
                elements = [
                    tp.Text("Width:"),
                    self.w,
                    tp.Text("Height:"),
                    self.h,
                ]
                self.group = tp.Group(elements, mode="h")
            else:
                elements = [tp.Text("Unsupported shape type")]
                self.group = tp.Group(elements, mode="h")
        self.box = tp.Box([self.group])
        self.launcher = self.box.get_updater()

    def on__init(self, rect: pygame.Rect, top_margin):
        self.rect = rect
        self.width = rect.width
        self.offset = self.width
        self.top_margin = rect.bottom

    def update(self):
        target_offset = 0 if self.visible else self.screen.get_width()
        if abs(self.offset - target_offset) > 1:
            self.offset += (target_offset - self.offset) / self.speed
        x = self.screen.get_width() - self.width + int(self.offset)
        self.box.set_topleft(x, self.top_margin)
        self.launcher.reaction(pygame.event.get())
        self.launcher.update()

    def show(self, shape_type: str) -> None:
        self.visible = self.shape_type == shape_type

    def hide(self):
        self.visible = False
