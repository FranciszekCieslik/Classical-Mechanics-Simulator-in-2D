import pygame
import pygame.gfxdraw


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

    def deactivate_drawing(self):
        '''Deactivate drawing mode.'''
        if self.state == 'triangle' and self.third_triangel_point is None:
            return
        self.is_drawing = False
        self.state = "empty"
        self.start_pos = None
        self.current_pos = None
        self.third_triangel_point = None

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
