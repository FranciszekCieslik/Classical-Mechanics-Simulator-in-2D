import math
from typing import Tuple

import pygame  # type: ignore
import pygame.gfxdraw
from obj.camera import Camera


class Circle:
    def __init__(
        self,
        surface: pygame.Surface,
        cam: Camera,
        position: pygame.Vector2,
        color: pygame.Vector3,
        radius: float,
        cell_size: int,
        angle: float = 0.0,
    ) -> None:
        self.surface: pygame.Surface = surface
        self.cam: Camera = cam
        self.position: pygame.Vector2 = pygame.Vector2(position[0], position[1])
        self.color: pygame.Vector3 = color
        self.radius: float = radius
        self.base_cell_size_world: float = cell_size
        self.screen_center = pygame.Vector2(0, 0)
        self.screen_radius = 0.0
        self.angle = angle
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
            int(self.screen_radius),
            self.color,
        )
        if self.cam.zoom <= 10:
            pygame.gfxdraw.aacircle(
                self.surface,
                int(self.screen_center.x),
                int(self.screen_center.y),
                int(self.screen_radius),
                self.border_color,
            )
        self._draw_radius_line()

    def _draw_radius_line(self) -> None:
        """Draws a line representing the radius direction."""
        radius_px = self.radius * self.base_cell_size_world * self.cam.zoom
        angle_rad = math.radians(self.angle)

        start = pygame.Vector2(self.screen_center)
        end = pygame.Vector2(
            start.x + math.cos(angle_rad) * radius_px,
            start.y - math.sin(angle_rad) * radius_px,  # - bo pygame ma oś Y w dół
        )

        pygame.gfxdraw.line(
            self.surface,
            int(start.x),
            int(start.y),
            int(end.x),
            int(end.y),
            self.border_color,
        )

    def move(self, dx: float, dy: float) -> None:
        self.position.x += dx
        self.position.y += dy

    def rotate(self, delta_angle: float) -> None:
        """Rotates the circle by a given angle (in degrees)."""
        self.angle = (self.angle + delta_angle) % 360

    def set_angle(self, angle: float) -> None:
        """Sets the absolute rotation angle (in degrees)."""
        self.angle = angle % 360

    def update(self) -> bool:
        """
        Updates the screen position and radius of the circle according to the camera.
        Returns False if the object is outside the visible area.
        """
        # world → pixels
        world_pos_px = pygame.Vector2(self.position) * self.base_cell_size_world
        world_radius_px = self.radius * self.base_cell_size_world

        # world → screen
        self.screen_center = self.cam.world_to_screen(world_pos_px)
        self.screen_radius = world_radius_px * self.cam.zoom

        # visibility check
        screen_w, screen_h = self.surface.get_size()
        x, y = self.screen_center
        r = self.screen_radius

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
        return distance_sq <= self.screen_radius * self.screen_radius
