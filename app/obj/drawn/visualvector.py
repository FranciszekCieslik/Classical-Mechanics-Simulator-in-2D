import math

import pygame
from Box2D import b2Vec2
from obj.camera import Camera


class VisualVector:
    def __init__(
        self,
        att_point: b2Vec2,
        value: b2Vec2,
        color: pygame.Color,
        camera: Camera,
        base_cell_size: int,
    ) -> None:
        self.screen = pygame.display.get_surface()
        self.attachment_point = att_point
        self.value = value
        self.color = color
        self.camera = camera
        self.base_cell_size = base_cell_size
        self.visible: bool = False
        self.line_thikness: int = 3

        self.scale_factor: float = 1.0
        self.label: str = ""
        self.unit: str = "Unit"

        # <-- ADDED: preloaded font
        self.font = pygame.font.SysFont("consolas", 14)

    def set_value(self, val: b2Vec2) -> None:
        self.value = val

    def draw(self) -> None:
        if not self.visible:
            return

        start_world = pygame.Vector2(self.attachment_point.x, self.attachment_point.y)
        start_screen = (
            start_world * self.base_cell_size * self.camera.zoom + self.camera.offset
        )

        scaled_value = (
            pygame.Vector2(self.value.x, self.value.y)
            * self.base_cell_size
            * self.camera.zoom
            * self.scale_factor
        )

        end_screen = start_screen + scaled_value

        if (
            not math.isfinite(start_screen.x)
            or not math.isfinite(start_screen.y)
            or not math.isfinite(end_screen.x)
            or not math.isfinite(end_screen.y)
        ):
            print("INVALID VECTOR:", start_screen, scaled_value, end_screen, self.value)
            return

        pygame.draw.line(
            self.screen,
            self.color,
            (int(start_screen.x), int(start_screen.y)),
            (int(end_screen.x), int(end_screen.y)),
            self.line_thikness,
        )

        arrow_vec = scaled_value
        if arrow_vec.length() > 0.0001:
            direction = arrow_vec.normalize()
            perp = pygame.Vector2(-direction.y, direction.x)

            head_length = 12
            head_width = 7

            left_head = end_screen - direction * head_length + perp * head_width
            right_head = end_screen - direction * head_length - perp * head_width

            pygame.draw.polygon(
                self.screen,
                self.color,
                [
                    (int(end_screen.x), int(end_screen.y)),
                    (int(left_head.x), int(left_head.y)),
                    (int(right_head.x), int(right_head.y)),
                ],
            )
            self._prep_label()
            if self.label:
                text_surface = self.font.render(self.label, True, self.color)
                offset = pygame.Vector2(10, -10)
                label_pos = end_screen + offset
                bg = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
                bg.fill((255, 255, 255, 120))  # półprzezroczyste tło
                self.screen.blit(bg, label_pos)
                self.screen.blit(text_surface, label_pos)

    def update(self, att_point: b2Vec2, value: b2Vec2) -> None:
        self.value = value
        self.attachment_point = att_point

    def _prep_label(self):
        value_magnitude = self._vector_value(self.value)
        self.label = f"{value_magnitude:.2f} {self.unit}"

    def _vector_value(self, vec: b2Vec2) -> float:
        return (vec.x**2 + vec.y**2) ** 0.5
