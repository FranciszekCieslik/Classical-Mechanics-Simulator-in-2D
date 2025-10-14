import math

import pygame  # type: ignore


def format_label_value(val, step_world):
    if step_world >= 1:
        return f"{int(round(val))}"
    # policz liczbę miejsc dziesiętnych potrzebnych dla step_world
    decimals = max(0, -int(math.floor(math.log10(step_world))))
    decimals = min(decimals, 6)  # cap
    fmt = f"{{:.{decimals}f}}"
    s = fmt.format(val)
    # obetnij trailing zeros
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return s


class Axes:
    def __init__(self, screen, grid):
        self.screen = screen
        self.grid = grid
        self.color = (50, 50, 50)
        self.font = pygame.font.SysFont("consolas", 14)
        self.visible = True

    def draw(self):
        if not self.visible or self.grid.camera is None:
            return

        width, height = self.screen.get_size()
        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        cam = self.grid.camera
        zoom = cam.zoom
        ox, oy = cam.offset
        base = self.grid.base_cell_size

        from math import floor, log10

        world_step = 1.0
        target_px = 100
        raw = target_px / (base * zoom)
        if raw <= 0:
            world_step = 1.0
        else:
            exp = math.floor(math.log10(raw))
            base_pow = 10**exp
            candidates = [1 * base_pow, 2 * base_pow, 5 * base_pow, 10 * base_pow]
            best = candidates[0]
            best_diff = abs((base * zoom * best) - target_px)
            for c in candidates[1:]:
                diff = abs((base * zoom * c) - target_px)
                if diff < best_diff:
                    best, best_diff = c, diff
            world_step = best

        step_px = base * zoom * world_step

        # pozycje osi (w pixelach)
        y_axis_x = ox  # bo screen_x = world_x*zoom + offset -> dla world_x=0 screen_x = offset.x
        x_axis_y = oy

        # rysuj grubsze linie osi
        if 0 <= y_axis_x < width:
            pygame.draw.line(surface, self.color, (y_axis_x, 0), (y_axis_x, height), 2)
        if 0 <= x_axis_y < height:
            pygame.draw.line(surface, self.color, (0, x_axis_y), (width, x_axis_y), 2)

        # etykiety osi X (poziome) — iteruj po indeksach kroków
        first_x_idx = math.floor((-ox) / step_px) - 1
        last_x_idx = math.ceil((width - ox) / step_px) + 1
        drawn_positions = set()
        for i in range(first_x_idx, last_x_idx + 1):
            x = ox + i * step_px
            if not (0 <= x < width):
                continue
            val = i * world_step  # wartość w jednostkach świata
            # unikaj podwójnego rysowania etykiety w tej samej pozycji pikselowej
            key = round(x)
            if key in drawn_positions:
                continue
            drawn_positions.add(key)
            label_text = format_label_value(val, world_step)
            label = self.font.render(label_text, True, self.color)
            # rysuj tuż pod osią X
            label_x = x - label.get_width() // 2
            label_y = x_axis_y + 6
            # upewnij się, że etykieta nie wychodzi poza ekran
            if 0 <= label_x + label.get_width() and label_x < width:
                surface.blit(label, (label_x, label_y))

        # etykiety osi Y (pionowe)
        first_y_idx = math.floor((-oy) / step_px) - 1
        last_y_idx = math.ceil((height - oy) / step_px) + 1
        drawn_positions.clear()
        for j in range(first_y_idx, last_y_idx + 1):
            y = oy + j * step_px
            if not (0 <= y < height):
                continue
            val = -j * world_step  # patrz orientacja: rosną w dół
            key = round(y)
            if key in drawn_positions:
                continue
            drawn_positions.add(key)
            label_text = format_label_value(val, world_step)
            label = self.font.render(label_text, True, self.color)
            label_x = y_axis_x + 6
            label_y = y - label.get_height() // 2
            # upewnij się, że etykieta nie wychodzi poza ekran
            if 0 <= label_y + label.get_height() and label_y < height:
                surface.blit(label, (label_x, label_y))

        self.screen.blit(surface, (0, 0))
