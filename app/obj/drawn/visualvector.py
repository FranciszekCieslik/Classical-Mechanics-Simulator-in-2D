import pygame
from Box2D import b2Vec2
from obj.camera import Camera


class VisualVector:
    def __init__(
        self,
        att_point: b2Vec2,
        value: b2Vec2,
        color: pygame.Color,
        camera: Camera,
        base_cell_size: int,
    ) -> None:
        self.screen = pygame.display.get_surface()
        self.attachment_point = att_point
        self.value = value
        self.color = color
        self.camera = camera
        self.base_cell_size = base_cell_size
        self.visible: bool = False
        self.line_thikness: int = 3

    def set_value(self, val: b2Vec2) -> None:
        self.value = val

    def draw(self) -> None:
        if not self.visible:
            return

        # --- 1. Współrzędne świata na ekran ---
        # Punkt przyłożenia (początek strzałki)
        start_world = pygame.Vector2(self.attachment_point.x, self.attachment_point.y)
        start_screen = (
            start_world * self.base_cell_size * self.camera.zoom + self.camera.offset
        )

        # --- 2. Przeskalowany wektor wartości ---
        # Wektor w metrach → w piksele
        scaled_value = (
            pygame.Vector2(self.value.x, self.value.y)
            * self.base_cell_size
            * self.camera.zoom
        )

        # --- 3. Koniec wektora na ekranie ---
        end_screen = start_screen + scaled_value

        # --- 4. Narysuj linię (trzon strzałki) ---
        pygame.draw.line(
            self.screen,
            self.color,
            (int(start_screen.x), int(start_screen.y)),
            (int(end_screen.x), int(end_screen.y)),
            self.line_thikness,
        )

        # --- 5. Narysuj grot strzałki ---
        # Określ kąt i długość grotu
        arrow_vec = scaled_value
        if arrow_vec.length() > 0.0001:
            direction = arrow_vec.normalize()
            perp = pygame.Vector2(-direction.y, direction.x)

            head_length = 12 * self.camera.zoom  # długość grotu
            head_width = 7 * self.camera.zoom  # szerokość grotu

            left_head = end_screen - direction * head_length + perp * head_width
            right_head = end_screen - direction * head_length - perp * head_width

            pygame.draw.polygon(
                self.screen,
                self.color,
                [
                    (int(end_screen.x), int(end_screen.y)),
                    (int(left_head.x), int(left_head.y)),
                    (int(right_head.x), int(right_head.y)),
                ],
            )

    def update(self, att_point: b2Vec2, value: b2Vec2) -> None:
        self.value = value
        self.attachment_point = att_point
