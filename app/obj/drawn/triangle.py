import math
from typing import Tuple

import pygame  # type: ignore
import pygame.gfxdraw
from obj.camera import Camera


class Triangle:
    def __init__(
        self,
        surface: pygame.Surface,
        cam: Camera,
        position: pygame.Vector2,
        color: pygame.Vector3,
        vertices: list[pygame.Vector2],
        cell_size: int,
        angle: float = 0.0,
    ) -> None:
        """
        Args:
            surface: pygame.Surface — drawing target
            cam: Camera — used for world→screen conversion
            position: pygame.Vector2 — world-space position of the triangle center
            color: pygame.Vector3 — RGB color
            vertices: list of 3 points relative to position, in world units
            cell_size: scaling from world→pixels
            angle: initial rotation in degrees
        """
        self.surface: pygame.Surface = surface
        self.cam: Camera = cam
        self.position: pygame.Vector2 = pygame.Vector2(position)
        self.color: pygame.Vector3 = color
        self.vertices: list[pygame.Vector2] = [pygame.Vector2(v) for v in vertices]
        self.base_cell_size_world: float = cell_size
        self.angle: float = angle
        self.border_color: pygame.Vector3 = pygame.Vector3(color / 2)
        self.border_width: int = 2
        self.screen_points: list[pygame.Vector2] = []
        self.is_visible: bool = True

    # ------------------------------------------------------------
    def draw(self) -> None:
        if not self.update():
            return

        points_int = [(int(p.x), int(p.y)) for p in self.screen_points]

        # Fill (antialiased polygon)
        pygame.gfxdraw.filled_polygon(self.surface, points_int, self.color)
        pygame.gfxdraw.aapolygon(self.surface, points_int, self.color)

        # Outline (border)
        pygame.gfxdraw.aapolygon(self.surface, points_int, self.border_color)

    # ------------------------------------------------------------
    def move(self, dx: float, dy: float) -> None:
        """Moves the triangle in world coordinates."""
        self.position.x += dx
        self.position.y += dy

    # ------------------------------------------------------------
    def set_angle(self, angle: float) -> None:
        """Sets an absolute rotation angle (in degrees)."""
        self.angle = angle % 360

    # ------------------------------------------------------------
    def _rotate_vertex(
        self, vertex: pygame.Vector2, angle_deg: float
    ) -> pygame.Vector2:
        """Rotates a local vertex around the origin by a given angle."""
        angle_rad = math.radians(angle_deg)
        cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
        return pygame.Vector2(
            vertex.x * cos_a - vertex.y * sin_a,
            vertex.x * sin_a + vertex.y * cos_a,
        )

    # ------------------------------------------------------------
    def update(self) -> bool:
        """
        Updates the screen coordinates of the triangle according to the camera and rotation.
        Returns False if the triangle is fully outside the screen.
        """
        self.screen_points = []

        for v in self.vertices:
            # Rotate local vertex
            rotated_v = self._rotate_vertex(v, self.angle)

            # Transform to world space and then to pixels
            world_vertex = self.position + rotated_v
            screen_vertex = self.cam.world_to_screen(
                world_vertex * self.base_cell_size_world
            )
            self.screen_points.append(screen_vertex)

        # Visibility check (bounding box)
        xs = [p.x for p in self.screen_points]
        ys = [p.y for p in self.screen_points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        screen_w, screen_h = self.surface.get_size()
        visible = max_x >= 0 and min_x <= screen_w and max_y >= 0 and min_y <= screen_h
        self.is_visible = visible
        return visible

    def set_position(self, position: pygame.Vector2) -> None:
        """Sets the absolute position of the triangle in world coordinates."""
        self.position = pygame.Vector2(position)

    def is_point_inside(self, point: Tuple[int, int]) -> bool:
        """Checks if a given point (in screen coordinates) is inside the triangle."""
        if not self.is_visible:
            return False

        # Using barycentric coordinates to check if the point is inside the triangle
        p = pygame.Vector2(point)
        a, b, c = self.screen_points

        # Vectors
        v0 = c - a
        v1 = b - a
        v2 = p - a

        # Dot products
        dot00 = v0.dot(v0)
        dot01 = v0.dot(v1)
        dot02 = v0.dot(v2)
        dot11 = v1.dot(v1)
        dot12 = v1.dot(v2)

        # Barycentric coordinates
        denom = dot00 * dot11 - dot01 * dot01
        if denom == 0:
            return False  # Degenerate triangle

        inv_denom = 1 / denom
        u = (dot11 * dot02 - dot01 * dot12) * inv_denom
        v = (dot00 * dot12 - dot01 * dot02) * inv_denom

        # Check if point is in triangle
        return (u >= 0) and (v >= 0) and (u + v <= 1)
