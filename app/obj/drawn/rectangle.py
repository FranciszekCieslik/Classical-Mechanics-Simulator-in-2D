import math
from typing import Tuple

import pygame
import pygame.gfxdraw
from obj.camera import Camera


class Rectangle:
    def __init__(
        self,
        surface: pygame.Surface,
        cam: Camera,
        position: pygame.Vector2,
        color: pygame.Vector3,
        size: pygame.Vector2,
        cell_size: int,
        angle: float = 0.0,
    ) -> None:
        """
        Rectangle with support for world coordinates, rotation and outline.

        Args:
            surface: pygame surface to draw on
            cam: camera transforming world to screen coordinates
            position: world position (center)
            color: fill color (RGB)
            size: rectangle size (width, height) in world units
            cell_size: world unit size (pixels)
            angle: rotation angle in degrees
            border_color: optional border color
            border_width: border thickness (only if border_color is set)
        """
        self.surface = surface
        self.cam = cam
        self.position = pygame.Vector2(position)
        self.color = color
        self.size = pygame.Vector2(size)
        self.base_cell_size_world = cell_size
        self.angle = angle
        self.border_color = pygame.Vector3(color / 2)
        self.border_width = 4
        self.is_visible: bool = True
        self.points_screen: list[tuple[float, float]] = []  # rotated points on screen

    # ------------------------------------------------------
    def rotate_point(
        self, point: pygame.Vector2, center: pygame.Vector2, angle_deg: float
    ) -> pygame.Vector2:
        """Rotate a point around a given center by `angle_deg` degrees."""
        angle_rad = math.radians(angle_deg)
        dx, dy = point.x - center.x, point.y - center.y
        qx = center.x + dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
        qy = center.y + dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
        return pygame.Vector2(qx, qy)

    # ------------------------------------------------------
    def update(self) -> bool:
        """
        Updates the screen-space coordinates of the rectangle.
        Returns False if the rectangle is outside the screen view.
        """
        # --- convert to pixels ---
        world_pos_px = self.position * self.base_cell_size_world
        world_size_px = self.size * self.base_cell_size_world

        # --- screen-space position ---
        screen_center = self.cam.world_to_screen(world_pos_px)
        screen_size = world_size_px * self.cam.zoom
        w, h = screen_size.x, screen_size.y

        # --- base corners (centered rectangle before rotation) ---
        half_w, half_h = w / 2, h / 2
        corners = [
            pygame.Vector2(screen_center.x - half_w, screen_center.y - half_h),
            pygame.Vector2(screen_center.x + half_w, screen_center.y - half_h),
            pygame.Vector2(screen_center.x + half_w, screen_center.y + half_h),
            pygame.Vector2(screen_center.x - half_w, screen_center.y + half_h),
        ]

        # --- rotate corners around center ---
        self.points_screen = [
            self.rotate_point(p, screen_center, self.angle) for p in corners
        ]

        # --- visibility check ---
        screen_w, screen_h = self.surface.get_size()
        rect_bounds = pygame.Rect(
            min(p[0] for p in self.points_screen),
            min(p[1] for p in self.points_screen),
            max(p[0] for p in self.points_screen)
            - min(p[0] for p in self.points_screen),
            max(p[1] for p in self.points_screen)
            - min(p[1] for p in self.points_screen),
        )

        visible = (
            rect_bounds.right >= 0
            and rect_bounds.left <= screen_w
            and rect_bounds.bottom >= 0
            and rect_bounds.top <= screen_h
        )

        self.is_visible = visible

        return visible

    # ------------------------------------------------------
    def draw(self) -> None:
        """Draw the rectangle if visible."""
        if not self.update():
            return

        pygame.gfxdraw.filled_polygon(self.surface, self.points_screen, self.color)
        pygame.gfxdraw.aapolygon(self.surface, self.points_screen, self.color)
        pygame.gfxdraw.aapolygon(self.surface, self.points_screen, self.border_color)

    # ------------------------------------------------------
    def move(self, vec: pygame.Vector2) -> None:
        """Move the rectangle by dx, dy in world coordinates."""
        self.position += vec

    def set_position(self, position: pygame.Vector2) -> None:
        """
        Sets the position from Box2D coordinates.
        Converts meters → pixels and flips Y for Pygame.
        """
        # Box2D: Y rośnie w górę, Pygame: Y w dół
        self.position = position

    def set_angle(self, angle_radians: float) -> None:
        """
        Sets the rotation angle based on Box2D body angle (radians → degrees).
        """
        self.angle = (angle_radians) % 360

    def is_point_inside(self, point: Tuple[int, int]) -> bool:
        """Checks if a given screen point (x, y) is inside the rectangle."""
        if not self.is_visible:
            return False

        x, y = point
        n = len(self.points_screen)
        inside = False

        p1x, p1y = self.points_screen[0]
        for i in range(n + 1):
            p2x, p2y = self.points_screen[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside
