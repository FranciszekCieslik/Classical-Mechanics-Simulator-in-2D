import math
from decimal import Decimal, getcontext

import pygame
import pygame.gfxdraw
from obj.camera import Camera
from obj.grid import nice_world_step

getcontext().prec = 28


def decimal_places_for_step(step: float) -> int:
    d = Decimal(str(step))
    exponent = int(d.as_tuple().exponent)  # 👈 KLUCZOWE

    if exponent < 0:
        return -exponent
    return 0


def snap_value(val: float, zoom, cell_size) -> float:
    main_step = nice_world_step(cell_size, zoom, target_px=100)

    main_step_dec = Decimal(str(main_step))
    helper_step = main_step_dec / Decimal("5")

    val_dec = Decimal(str(val))

    snapped_units = (val_dec / helper_step).quantize(
        Decimal('1'), rounding="ROUND_HALF_UP"
    )
    snapped_dec = snapped_units * helper_step

    snapped_3 = snapped_dec.quantize(Decimal("0.001"), rounding="ROUND_HALF_UP")

    return float(snapped_3)


class DrawAssistance:
    def __init__(self, surface: pygame.Surface, cam: Camera, cell_size: int):
        self.surface: pygame.Surface = surface
        self.is_drawing: bool = False
        self.state: str = "empty"

        self.start_pos: tuple[int, int] | None = None
        self.current_pos: tuple[int, int] | None = None
        self.third_triangel_point: tuple[int, int] | None = None
        self.color: tuple[int, int, int] = (0, 255, 0)
        self.border_color: tuple[int, int, int] = (0, 200, 0)
        self.camera = cam
        self.cell_size = cell_size

    def draw(self):
        if self.state == "empty":
            return
        if self.state == 'rectangle':
            self.draw_rectangle()
        elif self.state == 'circle':
            self.draw_circle()
        elif self.state == 'triangle':
            self.draw_triangle()
        elif self.state == 'point_particle':
            self.draw_point_particle()

    def active_drawing(self, state: str):
        '''Activate drawing mode with the given state by GUI button.'''
        self.is_drawing = True
        self.state = state

    def deactivate_drawing(self):
        '''Deactivate drawing mode.'''
        if self.start_pos is None or self.current_pos is None:
            return None
        if self.state == 'triangle' and self.third_triangel_point is None:
            return None
        data = self._prep_data()
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
        self.start_pos = self.snap_to_grid(pos)

    def set_current_position(self, pos: tuple[int, int]):
        if self.start_pos is None:
            return
        self.current_pos = self.snap_to_grid(pos)

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
            int(x1 + radius),
            int(y1),
            self.border_color,
        )

    def draw_triangle(self):
        if self.start_pos is None or self.current_pos is None:
            return

        x1, y1 = self.start_pos
        x2, y2 = self.current_pos

        point1 = pygame.Vector2(x1, y1)
        point2 = pygame.Vector2(x2, y2)
        if self.third_triangel_point is not None:
            point3 = self.third_triangel_point
        else:
            point3 = pygame.Vector2(x2, y1)

        corners = [point1, point2, point3]

        pygame.gfxdraw.filled_polygon(self.surface, corners, self.color)
        pygame.gfxdraw.aapolygon(self.surface, corners, self.color)
        pygame.gfxdraw.aapolygon(self.surface, corners, self.border_color)

    def set_third_triangle_point(self, pos: tuple[int, int] | None):
        if self.state != 'triangle' or self.third_triangel_point:
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

    def _prep_data(self):
        if self.state == "empty":
            return None

        if not self.start_pos or not self.current_pos:
            return None

        x1, y1 = self.start_pos
        x2, y2 = self.current_pos
        if self.state == "circle":
            r = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
            world_pos_px = (
                pygame.Vector2(x1, y1) - self.camera.offset
            ) / self.camera.zoom
            world_radius_px = r / self.camera.zoom
            position = world_pos_px / self.cell_size
            radius = world_radius_px / self.cell_size
            return position, snap_value(radius, self.camera.zoom, self.cell_size)

        elif self.state == "point_particle":
            world_pos_px = (
                pygame.Vector2(x2, y2) - self.camera.offset
            ) / self.camera.zoom
            position = world_pos_px / self.cell_size
            radius = 10
            return position, radius

        elif self.state == "line":
            world_p1_px = (
                pygame.Vector2(self.start_pos) - self.camera.offset
            ) / self.camera.zoom
            world_p2_px = (
                pygame.Vector2(self.current_pos) - self.camera.offset
            ) / self.camera.zoom
            world_p1 = world_p1_px / self.cell_size
            world_p2 = world_p2_px / self.cell_size
            return world_p1, world_p2

        elif self.state == "rectangle":
            screen_points = [
                pygame.Vector2(x1, y1),
                pygame.Vector2(x2, y1),
                pygame.Vector2(x2, y2),
                pygame.Vector2(x1, y2),
            ]
            world_points = [
                (p - self.camera.offset) / self.camera.zoom / self.cell_size
                for p in screen_points
            ]
            min_x = min(p.x for p in world_points)
            max_x = max(p.x for p in world_points)
            min_y = min(p.y for p in world_points)
            max_y = max(p.y for p in world_points)
            width = max_x - min_x
            height = max_y - min_y
            width = snap_value(width, self.camera.zoom, self.cell_size)
            height = snap_value(height, self.camera.zoom, self.cell_size)
            position = pygame.Vector2((min_x + max_x) / 2, (min_y + max_y) / 2)
            return position, (width, height)

        elif self.state == "triangle":
            point1 = pygame.Vector2(x1, y1)
            point2 = pygame.Vector2(x2, y2)
            point3 = pygame.Vector2(x2, y1)
            if self.third_triangel_point is not None:
                point3 = self.third_triangel_point
            points = [point1, point2, point3]
            screen_points = points
            world_points = [
                (p - self.camera.offset) / self.camera.zoom / self.cell_size
                for p in screen_points
            ]
            position = sum(world_points, pygame.Vector2()) / 3
            vertices = [wp - position for wp in world_points]
            return position, vertices

        return None

    def draw_point_particle(self):
        if self.start_pos is None or self.current_pos is None:
            return

        x1, y1 = self.current_pos

        radius = 10

        pygame.gfxdraw.filled_circle(self.surface, x1, y1, radius, self.color)
        pygame.gfxdraw.aacircle(self.surface, x1, y1, radius, self.color)
        pygame.gfxdraw.aacircle(self.surface, x1, y1, radius, self.border_color)

    def snap_to_grid(self, pos: tuple[int, int]) -> tuple[int, int]:
        """
        Zaokrągla podany punkt ekranu (px) do najbliższej linii głównej
        lub pomocniczej siatki rysowanej przez Grid.
        """

        x, y = pos
        ox, oy = self.camera.offset
        zoom = self.camera.zoom

        # --- to samo co w Grid.draw() ---
        world_step = self.cell_size  # base_cell_size = pixel przy zoom=1
        world_step = self.cell_size
        world_step = self.cell_size

        # używamy tego samego algorytmu
        step_world_unit = nice_world_step(self.cell_size, zoom, target_px=100)
        step_px = self.cell_size * zoom * step_world_unit

        helper_count = 5
        helper_px = step_px / helper_count if step_px >= 80 else None

        # --- snapowanie do linii ---
        def snap_axis(v, offset, step, helper):
            # pozycja w "przestrzeni siatki"
            grid_space = (v - offset) / step

            if helper is None:
                # tylko linie główne
                nearest_index = round(grid_space)
                snapped = offset + nearest_index * step
                return int(snapped)

            # linie pomocnicze = step/5 → czyli 1/5 indeksu jednostki
            fine_index = grid_space * helper_count
            nearest_fine = round(fine_index)
            snapped = offset + (nearest_fine / helper_count) * step
            return int(snapped)

        snap_x = snap_axis(x, ox, step_px, helper_px)
        snap_y = snap_axis(y, oy, step_px, helper_px)

        return (snap_x, snap_y)
