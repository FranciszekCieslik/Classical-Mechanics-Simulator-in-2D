import pygame
import pygame.gfxdraw


class DrawAssistance:
    def __init__(self, surface: pygame.Surface):
        self.surface: pygame.Surface = surface
        self.is_drawing: bool = False
        self.state: str = "empty"

        self.start_pos: tuple[int, int] | None = None
        self.current_pos: tuple[int, int] | None = None
        self.color: tuple[int, int, int] = (0, 255, 0)
        self.border_color: tuple[int, int, int] = (0, 200, 0)

    def draw(self):
        if self.state == "empty":
            return
        if self.state == 'rectangle':
            self.draw_rectangle()

    def active_drawing(self, state: str):
        '''Activate drawing mode with the given state by GUI button.'''
        self.is_drawing = True
        self.state = state

    def deactivate_drawing(self):
        '''Deactivate drawing mode.'''
        self.is_drawing = False
        self.state = "empty"
        self.start_pos = None
        self.current_pos = None

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
