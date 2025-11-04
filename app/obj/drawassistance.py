import math

import pygame
import pygame.gfxdraw
from obj.camera import Camera


class DrawAssistance:
    def __init__(self, surface: pygame.Surface):
        self.surface: pygame.Surface = surface
        self.is_drawing: bool = False
        self.state: str = "empty"

        self.start_pos: tuple[int, int] | None = None
        self.current_pos: tuple[int, int] | None = None
        self.third_triangel_point: tuple[int, int] | None = None
        self.color: tuple[int, int, int] = (0, 255, 0)
        self.border_color: tuple[int, int, int] = (0, 200, 0)

    def draw(self):
        if self.state == "empty":
            return
        if self.state == 'rectangle':
            self.draw_rectangle()
        elif self.state == 'circle':
            self.draw_circle()
        elif self.state == 'triangle':
            self.draw_triangle()
        elif self.state == 'line':
            self.draw_line()

    def active_drawing(self, state: str):
        '''Activate drawing mode with the given state by GUI button.'''
        self.is_drawing = True
        self.state = state

    def deactivate_drawing(self, cam: Camera, cell_size: float):
        '''Deactivate drawing mode.'''
        if self.start_pos is None or self.current_pos is None:
            return None
        if self.state == 'triangle' and self.third_triangel_point is None:
            return None
        data = self._prep_data(cam, cell_size)
        if data is None:
            return None
        pos, size = data
        state = self.state
        self.is_drawing = False
        self.state = "empty"
        self.start_pos = None
        self.current_pos = None
        self.third_triangel_point = None
        return state, pos, size, self.color

    def set_start_position(self, pos: tuple[int, int]):
        self.start_pos = pos

    def set_current_position(self, pos: tuple[int, int]):
        self.current_pos = pos

    def draw_rectangle(self):
        if self.start_pos is None or self.current_pos is None:
            return

        x1, y1 = self.start_pos
        x2, y2 = self.current_pos

        corners = [
            pygame.Vector2(x1, y1),
            pygame.Vector2(x2, y1),
            pygame.Vector2(x2, y2),
            pygame.Vector2(x1, y2),
        ]
        pygame.gfxdraw.filled_polygon(self.surface, corners, self.color)
        pygame.gfxdraw.aapolygon(self.surface, corners, self.color)
        pygame.gfxdraw.aapolygon(self.surface, corners, self.border_color)

    def draw_circle(self):
        if self.start_pos is None or self.current_pos is None:
            return

        x1, y1 = self.start_pos
        x2, y2 = self.current_pos

        radius = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)

        pygame.gfxdraw.filled_circle(self.surface, x1, y1, radius, self.color)
        pygame.gfxdraw.aacircle(self.surface, x1, y1, radius, self.color)
        pygame.gfxdraw.aacircle(self.surface, x1, y1, radius, self.border_color)
        pygame.gfxdraw.line(
            self.surface,
            int(x1),
            int(y1),
            int(x2),
            int(y2),
            self.border_color,
        )

    def draw_triangle(self):
        if self.start_pos is None or self.current_pos is None:
            return

        x1, y1 = self.start_pos
        x2, y2 = self.current_pos

        point1 = pygame.Vector2(x1, y1)
        point2 = pygame.Vector2(x2, y2)
        point3 = pygame.Vector2(x2, y1)
        if self.third_triangel_point is not None:
            point3 = self.third_triangel_point

        corners = [point1, point2, point3]

        pygame.gfxdraw.filled_polygon(self.surface, corners, self.color)
        pygame.gfxdraw.aapolygon(self.surface, corners, self.color)
        pygame.gfxdraw.aapolygon(self.surface, corners, self.border_color)

    def set_third_triangle_point(self, pos: tuple[int, int] | None):
        if self.state != 'triangle':
            return
        if pos is not None and self.start_pos is not None:
            self.third_triangel_point = (pos[0], self.start_pos[1])

    def draw_line(self):
        if self.start_pos is None or self.current_pos is None:
            return

        x1, y1 = self.start_pos
        x2, y2 = self.current_pos

        pygame.gfxdraw.line(self.surface, x1, y1, x2, y2, self.color)
        pygame.gfxdraw.line(self.surface, x1, y1, x2, y2, self.border_color)

    def set_color(self, color: pygame.Vector3):
        self.color = color
        self.border_color = pygame.Vector3(color / 2)

    def _prep_data(self, cam: Camera, cell_size: float):
        if self.state == "empty":
            return None

        if not self.start_pos or not self.current_pos:
            return None

        x1, y1 = self.start_pos
        x2, y2 = self.current_pos
        if self.state == "circle":
            r = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
            world_pos_px = (pygame.Vector2(x1, y1) - cam.offset) / cam.zoom
            world_radius_px = r / cam.zoom
            position = world_pos_px / cell_size
            radius = world_radius_px / cell_size
            return position, radius

        elif self.state == "line":
            world_p1_px = (pygame.Vector2(self.start_pos) - cam.offset) / cam.zoom
            world_p2_px = (pygame.Vector2(self.current_pos) - cam.offset) / cam.zoom
            world_p1 = world_p1_px / cell_size
            world_p2 = world_p2_px / cell_size
            return world_p1, world_p2

        elif self.state == "rectangle":
            left = min(x1, x2)
            right = max(x1, x2)
            top = min(y1, y2)
            bottom = max(y1, y2)
            screen_points = [
                pygame.Vector2(x1, y1),
                pygame.Vector2(x2, y1),
                pygame.Vector2(x2, y2),
                pygame.Vector2(x1, y2),
            ]
            world_points = [
                (p - cam.offset) / cam.zoom / cell_size for p in screen_points
            ]
            min_x = min(p.x for p in world_points)
            max_x = max(p.x for p in world_points)
            min_y = min(p.y for p in world_points)
            max_y = max(p.y for p in world_points)
            width = max_x - min_x
            height = max_y - min_y
            position = pygame.Vector2((min_x + max_x) / 2, (min_y + max_y) / 2)
            return position, (width, height)

        elif self.state == "triangle":
            point1 = pygame.Vector2(x1, y1)
            point2 = pygame.Vector2(x2, y2)
            point3 = pygame.Vector2(x2, y1)
            if self.third_triangel_point is not None:
                point3 = self.third_triangel_point
            points = [point1, point2, point3]
            points = [pygame.Vector2(p) for p in points]
            # --- sort ---
            centroid = sum(points, pygame.Vector2()) / 3
            points_sorted = sorted(
                points, key=lambda p: math.atan2(p.y - centroid.y, p.x - centroid.x)
            )
            top_point = min(points_sorted, key=lambda p: p.y)
            while points_sorted[0] != top_point:
                points_sorted.append(points_sorted.pop(0))
            # ---
            screen_points = points_sorted
            world_points = [
                (p - cam.offset) / cam.zoom / cell_size for p in screen_points
            ]
            position = sum(world_points, pygame.Vector2()) / 3
            vertices = [wp - position for wp in world_points]
            return position, vertices

        return None
