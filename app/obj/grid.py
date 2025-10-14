import math

import pygame  # type: ignore


def nice_world_step(base_pixel, zoom, target_px=100):
    """
    base_pixel: base_cell_size (piksele przy zoom=1)
    zoom: aktualny zoom
    target_px: docelowa długość w px dla jednego kroku jednostki świata
    zwraca: step_in_world_units (np. 1, 2, 5, 10, 0.1, ...)
    """
    raw = target_px / (base_pixel * zoom)
    if raw <= 0:
        return 1.0
    exp = math.floor(math.log10(raw))
    base = 10**exp
    candidates = [1 * base, 2 * base, 5 * base, 10 * base]
    best = candidates[0]
    best_diff = abs((base_pixel * zoom * best) - target_px)
    for c in candidates[1:]:
        diff = abs((base_pixel * zoom * c) - target_px)
        if diff < best_diff:
            best, best_diff = c, diff
    return best


class Grid:
    def __init__(self, screen, cell_size=50, color=(60, 60, 60), camera=None):
        self.screen = screen
        self.color = color
        self.camera = camera
        self.visible = True
        self.base_cell_size = cell_size
        self.surface = pygame.Surface(
            pygame.display.get_desktop_sizes()[0], pygame.SRCALPHA
        )

    def resize(self):
        size = self.screen.get_size()
        self.surface = pygame.Surface(size, pygame.SRCALPHA)

    def draw(self):
        if not self.visible or self.camera is None:
            return

        zoom = self.camera.zoom
        size = self.screen.get_size()
        if self.surface.get_size() != size:
            self.surface = pygame.Surface(size, pygame.SRCALPHA)

        width, height = self.surface.get_size()
        ox, oy = self.camera.offset
        self.surface.fill((0, 0, 0, 0))

        world_step = nice_world_step(self.base_cell_size, zoom, target_px=100)
        step_px = self.base_cell_size * zoom * world_step

        helper_count = 5
        helper_px = step_px / helper_count if step_px >= 80 else None

        first_x_idx = math.floor((-ox) / step_px) - 1
        last_x_idx = math.ceil((width - ox) / step_px) + 1
        first_y_idx = math.floor((-oy) / step_px) - 1
        last_y_idx = math.ceil((height - oy) / step_px) + 1

        if helper_px is not None and helper_px >= 2:
            # rysuj pionowe helpery
            for i in range(first_x_idx * helper_count, last_x_idx * helper_count):
                x = ox + (i / helper_count) * step_px
                if i % helper_count == 0:
                    continue
                if 0 <= x < width:
                    pygame.draw.line(
                        self.surface, (200, 200, 200, 200), (x, 0), (x, height)
                    )
            # rysuj poziome helpery
            for j in range(first_y_idx * helper_count, last_y_idx * helper_count):
                y = oy + (j / helper_count) * step_px
                if j % helper_count == 0:
                    continue
                if 0 <= y < height:
                    pygame.draw.line(
                        self.surface, (200, 200, 200, 200), (0, y), (width, y)
                    )

        # rysuj linie główne
        for i in range(first_x_idx, last_x_idx + 1):
            x = ox + i * step_px
            if 0 <= x < width:
                pygame.draw.line(self.surface, self.color, (x, 0), (x, height))
        for j in range(first_y_idx, last_y_idx + 1):
            y = oy + j * step_px
            if 0 <= y < height:
                pygame.draw.line(self.surface, self.color, (0, y), (width, y))

        self.screen.blit(self.surface, (0, 0))
