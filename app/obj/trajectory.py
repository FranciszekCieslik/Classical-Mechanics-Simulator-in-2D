from typing import Any, Optional

import pygame
import pygame.gfxdraw
from Box2D import b2Vec2
from obj.camera import Camera


def _vectors_are_close(
    p1: pygame.Vector2, p2: pygame.Vector2, eps: float = 1e-2
) -> bool:
    return p1.distance_to(p2) < eps


class Trajectory:
    def __init__(
        self, camera: Camera, color: pygame.Color, base_cell_size: int, body: Any
    ):
        self.camera = camera
        # Rozjaśnij kolor bez przekroczenia 255
        self.light_color = tuple(min(c + 100, 255) for c in color[:3])
        self.dark_color = tuple(max(c - 50, 0) for c in color[:3])
        self.line_thickness: int = 2
        self.base_cell_size = base_cell_size
        self.surface: pygame.Surface = pygame.display.get_surface()
        self.visible: bool = False
        self.trajectory_points: list[pygame.Vector2] = []
        self.body = body

    # TRAJECTORY MANAGEMENT
    def add_trajectory_point(self, point: pygame.Vector2) -> None:
        n_point = self._create_trajectory_point(point)
        if n_point not in self.trajectory_points:
            self.trajectory_points.append(n_point)

    def _create_trajectory_point(self, point: pygame.Vector2) -> pygame.Vector2:
        return pygame.Vector2(round(point.x, 3), round(point.y, 3))

    def _check_if_trajectory_changed(self, start_point: pygame.Vector2) -> bool:
        """Return True if trajectory has changed."""
        if not self.trajectory_points:
            return True
        if not _vectors_are_close(self.trajectory_points[0], start_point):
            return True

        predict_tra = self._predict_trajectory(self.body)
        if not predict_tra:
            return False

        N = min(len(predict_tra), len(self.trajectory_points), 20)
        for i in range(0, N):
            if not _vectors_are_close(predict_tra[i], self.trajectory_points[i]):
                return True

        return False

    # COORDINATE CONVERSIONS
    def _point_to_screen(self, point: pygame.Vector2) -> pygame.Vector2:
        screen_x = (
            point.x * self.base_cell_size * self.camera.zoom + self.camera.offset.x
        )
        screen_y = (
            point.y * self.base_cell_size * self.camera.zoom + self.camera.offset.y
        )
        return pygame.Vector2(screen_x, screen_y)

    def _if_point_on_screen(self, point: pygame.Vector2) -> bool:
        """Zwraca True, jeśli punkt (w świecie) jest widoczny na ekranie."""
        screen_pos = self._point_to_screen(point)
        w, h = self.surface.get_size()
        return 0 <= screen_pos.x <= w and 0 <= screen_pos.y <= h

    # PHYSICS PREDICTION
    def _predict_trajectory(
        self, body: Any, dt: float = 1 / 60, steps: int = 60
    ) -> Optional[list[pygame.Vector2]]:
        if not body.awake:
            return None

        g = body.world.gravity
        if hasattr(g, "x") and hasattr(g, "y"):
            gravity = pygame.Vector2(g.x, g.y)
        else:
            gravity = pygame.Vector2(0, -9.81)

        pos = pygame.Vector2(body.position.x, body.position.y)
        vel = pygame.Vector2(body.linearVelocity.x, body.linearVelocity.y)
        mass = body.mass

        trajectory = [pos.copy()]
        for _ in range(steps):
            force = mass * gravity
            acc = force / mass

            vel += acc * dt
            pos += vel * dt
            trajectory.append(pos.copy())

        return trajectory

    # RENDERING
    def draw_predict_trajectory(self, skip: int = 2):
        """
        Rysuje przewidywaną trajektorię obiektu.
        :param skip: liczba punktów do pominięcia (np. 2 = rysuj co 2 punkt)
        """

        # Przewiduj nową trajektorię
        predict_tra = self._predict_trajectory(self.body)
        if predict_tra is None:
            return

        predict_tra = [self._create_trajectory_point(p) for p in predict_tra]

        points = [
            self._point_to_screen(p) for p in predict_tra if self._if_point_on_screen(p)
        ]

        if skip > 1:
            points = points[::skip]

        if len(points) < 2:
            return

        int_points = [(int(p.x), int(p.y)) for p in points]

        for i in range(len(int_points) - 1):
            x1, y1 = int_points[i]
            x2, y2 = int_points[i + 1]

            if self.line_thickness > 1:
                pygame.draw.line(
                    self.surface,
                    self.light_color,
                    (x1, y1),
                    (x2, y2),
                    self.line_thickness,
                )

            pygame.gfxdraw.line(self.surface, x1, y1, x2, y2, self.light_color)

    def draw_track(self, start_point: pygame.Vector2, skip: int = 2):
        pos = pygame.Vector2(self.body.position.x, self.body.position.y)
        self.add_trajectory_point(pos)
        points = [
            self._point_to_screen(p)
            for p in self.trajectory_points
            if self._if_point_on_screen(p)
        ]
        if skip > 1:
            points = points[::skip]
        if len(points) < 2:
            return

        int_points = [(int(p.x), int(p.y)) for p in points]

        for i in range(len(int_points) - 1):
            x1, y1 = int_points[i]
            x2, y2 = int_points[i + 1]

            if self.line_thickness > 1:
                pygame.draw.line(
                    self.surface,
                    self.dark_color,
                    (x1, y1),
                    (x2, y2),
                    self.line_thickness,
                )
            pygame.gfxdraw.line(self.surface, x1, y1, x2, y2, self.dark_color)

    def draw_trajectory(self, start_point: pygame.Vector2, skip: int = 2):
        if not self.visible:
            return
        self.draw_track(start_point, skip)
        self.draw_predict_trajectory(skip)

    def clear_track(self):
        self.trajectory_points = []
