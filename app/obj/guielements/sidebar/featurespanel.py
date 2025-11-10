from typing import Any, Optional, Tuple

import pygame
import thorpy as tp


class FeaturesPanel:
    def __init__(self) -> None:
        self.screen: pygame.Surface = pygame.display.get_surface()
        self.visible: bool = False
        self.speed: int = 12
        self.rect: Optional[pygame.Rect] = None
        self.width: Optional[int] = None
        self.offset: Optional[int] = None
        self.top_margin: Optional[int] = None
        # ---
        self.mass: tp.TextInput
        self.density: tp.TextInput
        self.friction: tp.TextInput
        self.restitution: tp.TextInput
        self.start_velocity_x: tp.TextInput
        self.start_velocity_y: tp.TextInput
        self.curr_velocity_x: tp.TextInput
        self.curr_velocity_y: tp.TextInput
        self.start_angular_velocity: tp.TextInput
        self.curr_angular_velocity: tp.TextInput

        # lista nazw wszystkich pól tekstowych
        fields = [
            "mass",
            "density",
            "friction",
            "restitution",
            "start_velocity_x",
            "start_velocity_y",
            "curr_velocity_x",
            "curr_velocity_y",
            "start_angular_velocity",
            "curr_angular_velocity",
        ]

        # automatyczna inicjalizacja
        for name in fields:
            text_input = tp.TextInput("", placeholder="00.00")
            text_input.set_only_numbers()
            setattr(self, name, text_input)

        elements = [
            tp.Line("h", 360),
            tp.Group(
                [
                    tp.Text("Mass:", font_size=14),
                    self.mass,
                    tp.Text("Density:", font_size=14),
                    self.density,
                ],
                "h",
            ),
            tp.Group(
                [
                    tp.Text("Friction:", font_size=14),
                    self.friction,
                    tp.Text("Restitution:", font_size=14),
                    self.restitution,
                ],
                "h",
            ),
            tp.Line("h", 360),
            tp.Text("Lineral Velocity", font_size=16),
            tp.Line("h", 360),
            tp.Group(
                [
                    tp.Text("Start:", font_size=14),
                    tp.Text("x:", font_size=14),
                    self.start_velocity_x,
                    tp.Text("y:", font_size=14),
                    self.start_velocity_y,
                ],
                "h",
            ),
            tp.Group(
                [
                    tp.Text("Current", font_size=14),
                    tp.Text("x:", font_size=14),
                    self.curr_velocity_x,
                    tp.Text("y:", font_size=14),
                    self.curr_velocity_y,
                ],
                "h",
            ),
            tp.Line("h", 360),
            tp.Text("Angular Velocity", font_size=16),
            tp.Line("h", 360),
            tp.Group(
                [tp.Text("Start:", font_size=14), self.start_angular_velocity],
                "h",
            ),
            tp.Group(
                [tp.Text("Current", font_size=14), self.curr_angular_velocity],
                "h",
            ),
        ]
        # ---
        self.group = tp.Group(elements, mode="v")
        self.box = tp.Box([self.group])
        self.box.set_bck_color((0, 0, 0))

    def rebuild(self, rect: pygame.Rect) -> None:
        self.rect = rect
        self.width = rect.width
        self.offset = self.width
        self.top_margin = rect.bottom
        self.box.set_size((self.width, self.box.rect.height))
        self.box.set_topleft(self.rect.left, self.top_margin)

    def show(self, val: str) -> None:
        if isinstance(val, list):
            val = val[0] if val else ''
        self.visible = val != 'static'

    def hide(self) -> None:
        self.visible = False

    def set_data_from_obj(
        self, body: Any, linearVelocity: Tuple[float, float], angularVelocity: float
    ) -> None:
        self.mass.value = str(round(body.mass, 3))
        self.density.value = str(round(body.fixtures[0].density, 3))
        self.friction.value = str(round(body.fixtures[0].friction, 3))
        self.restitution.value = str(round(body.fixtures[0].restitution, 3))

        self.start_velocity_x.value = str(round(linearVelocity[0], 3))
        self.start_velocity_y.value = str(round(linearVelocity[1], 3))
        self.curr_velocity_x.value = str(round(body.linearVelocity.x, 3))
        self.curr_velocity_y.value = str(round(body.linearVelocity.y, 3))

        self.start_angular_velocity.value = str(round(angularVelocity, 3))
        self.curr_angular_velocity.value = str(round(body.angularVelocity, 3))
