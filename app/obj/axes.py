import math

import pygame  # type: ignore
from obj.grid import Grid


def format_label_value(val: float, step_world: float) -> str:
    if step_world >= 1:
        return f"{int(round(val))}"
    decimals = max(0, -int(math.floor(math.log10(step_world))))
    decimals = min(decimals, 6)
    fmt = f"{{:.{decimals}f}}"
    s = fmt.format(val)
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return s


class Axes:
    def __init__(self, screen, grid: Grid):
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

        # --- wyznaczanie kroku w świecie ---
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

        # --- pozycje osi (w pikselach ekranu) ---
        y_axis_x = ox
        x_axis_y = oy

        # --- sprawdzanie widoczności osi ---
        x_axis_visible = 0 <= x_axis_y < height
        y_axis_visible = 0 <= y_axis_x < width

        # --- rysowanie osi Y ---
        if y_axis_visible:
            pygame.draw.line(surface, self.color, (y_axis_x, 0), (y_axis_x, height), 2)
            y_axis_draw_x = y_axis_x
        else:
            pygame.draw.line(surface, self.color, (0, 0), (0, height), 4)
            y_axis_draw_x = 0  # rysowana przy lewej krawędzi

        # --- rysowanie osi X ---
        if x_axis_visible:
            pygame.draw.line(surface, self.color, (0, x_axis_y), (width, x_axis_y), 2)
            x_axis_draw_y = x_axis_y
        else:
            pygame.draw.line(
                surface, self.color, (0, height - 1), (width, height - 1), 4
            )
            x_axis_draw_y = height - 1  # rysowana przy dolnej krawędzi

        # --- etykiety osi X ---
        first_x_idx = math.floor((-ox) / step_px) - 1
        last_x_idx = math.ceil((width - ox) / step_px) + 1
        drawn_positions = set()

        for i in range(first_x_idx, last_x_idx + 1):
            x = ox + i * step_px
            if not (0 <= x < width):
                continue
            val = i * world_step
            key = round(x)
            if key in drawn_positions:
                continue
            drawn_positions.add(key)
            label_text = format_label_value(val, world_step)
            label = self.font.render(label_text, True, self.color)

            label_x = x - label.get_width() // 2
            label_y = x_axis_draw_y + (6 if x_axis_visible else -label.get_height() - 6)
            if val == 0:
                label_x -= label.get_width() // 2
            if 0 <= label_x + label.get_width() and label_x < width:
                surface.blit(label, (label_x, label_y))

        # --- etykiety osi Y ---
        first_y_idx = math.floor((-oy) / step_px) - 1
        last_y_idx = math.ceil((height - oy) / step_px) + 1
        drawn_positions.clear()

        for j in range(first_y_idx, last_y_idx + 1):
            y = oy + j * step_px
            if not (0 <= y < height):
                continue

            val = -j * world_step
            if val == 0:
                continue

            key = round(y)
            if key in drawn_positions:
                continue
            drawn_positions.add(key)

            label_text = format_label_value(val, world_step)
            label = self.font.render(label_text, True, self.color)

            label_x = y_axis_draw_x + (6 if y_axis_visible else 6)
            label_y = y - label.get_height() // 2

            if 0 <= label_y + label.get_height() and label_y < height:
                surface.blit(label, (label_x, label_y))

        self.screen.blit(surface, (0, 0))
