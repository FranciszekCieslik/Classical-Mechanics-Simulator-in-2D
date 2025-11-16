import math
from typing import Tuple

import pygame  # type: ignore
import pygame.gfxdraw
from obj.camera import Camera
from obj.drawn.empty import Empty


class PointParticle(Empty):
    def __init__(
        self,
        surface: pygame.Surface,
        cam: Camera,
        position: pygame.Vector2,
        color: pygame.Vector3,
        cell_size: int,
    ) -> None:
        self.surface: pygame.Surface = surface
        self.cam: Camera = cam
        self.position: pygame.Vector2 = pygame.Vector2(position[0], position[1])
        self.color: pygame.Vector3 = color
        self.radius: float = 10
        self.base_cell_size_world: float = cell_size
        self.screen_center = pygame.Vector2(0, 0)
        self.border_color = pygame.Vector3(color / 2)
        self.border_width = 4
        self.is_visible: bool = True

    def draw(self) -> None:
        if not self.update():
            return
        pygame.gfxdraw.filled_circle(
            self.surface,
            int(self.screen_center.x),
            int(self.screen_center.y),
            int(self.radius),
            self.color,
        )

        pygame.gfxdraw.aacircle(
            self.surface,
            int(self.screen_center.x),
            int(self.screen_center.y),
            int(self.radius),
            self.border_color,
        )

    def move(self, vec: pygame.Vector2) -> None:
        """Move the rectangle by dx, dy in world coordinates."""
        self.position += vec

    def update(self) -> bool:
        """
        Updates the screen position and radius of the circle according to the camera.
        Returns False if the object is outside the visible area.
        """
        # world → pixels
        world_pos_px = pygame.Vector2(self.position) * self.base_cell_size_world

        # world → screen
        self.screen_center = self.cam.world_to_screen(world_pos_px)

        # visibility check
        screen_w, screen_h = self.surface.get_size()
        x, y = self.screen_center
        r = self.radius

        visible = x + r >= 0 and x - r <= screen_w and y + r >= 0 and y - r <= screen_h
        self.is_visible = visible
        return visible

    def set_position(self, position: pygame.Vector2) -> None:
        """Sets the absolute position of the triangle in world coordinates."""
        self.position = pygame.Vector2(position)

    def is_point_inside(self, point: Tuple[int, int]) -> bool:
        """Checks if a given point (in screen coordinates) is inside the circle."""
        if not self.is_visible:
            return False

        dx = point[0] - self.screen_center.x
        dy = point[1] - self.screen_center.y
        distance_sq = dx * dx + dy * dy
        return distance_sq <= 100
