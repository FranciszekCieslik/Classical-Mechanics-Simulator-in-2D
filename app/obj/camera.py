import pygame  # type: ignore


class Camera:
    def __init__(self):
        self.offset = pygame.Vector2(0, 0)  # ekran = world*zoom + offset
        self.zoom = 1.0  # płynny zoom
        self.min_zoom = 0.01
        self.max_zoom = 1000.0
        self.zoom_speed = 1.12  # multiplicative factor per scroll tick

    def zoom_at(self, factor, pivot):
        """Zoom multiplicative wokół pivotu (pivot w pikselach ekranu)."""
        old_zoom = self.zoom
        new_zoom = max(self.min_zoom, min(self.max_zoom, old_zoom * factor))

        if abs(new_zoom - old_zoom) < 1e-12:
            return

        # world position odpowiadający pivotowi przed zoomem:
        world_pos = (pygame.Vector2(pivot) - self.offset) / old_zoom

        # ustaw nowy zoom i policz offset tak, by pivot pozostał w tym samym miejscu ekranu
        self.zoom = new_zoom
        self.offset = pygame.Vector2(pivot) - world_pos * self.zoom

    def move(self, dx=0, dy=0):
        """Przesunięcie ekranu w pikselach (typu drag)."""
        self.offset.x += dx
        self.offset.y += dy

    # pomocnicze: przekształcenia
    def world_to_screen(self, world_pos):
        return pygame.Vector2(world_pos) * self.zoom + self.offset

    def screen_to_world(self, screen_pos):
        return (pygame.Vector2(screen_pos) - self.offset) / self.zoom
