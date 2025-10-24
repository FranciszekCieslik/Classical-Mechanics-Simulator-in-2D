import pygame  # type: ignore
from obj.camera import Camera


class Rectangle:
    def __init__(
        self,
        surface: pygame.Surface,
        cam: Camera,
        position: pygame.Vector2,
        color: pygame.Vector3,
        size: pygame.Vector2,
        cell_size: int,
    ) -> None:
        self.surface: pygame.Surface = surface
        self.cam: Camera = cam
        self.position: pygame.Vector2 = pygame.Vector2(
            position[0], position[1]
        )  # in world coordinates
        self.color: pygame.Vector3 = color
        self.size: pygame.Vector2 = size
        self.base_cell_size_world: float = cell_size
        self.rect = pygame.Rect(0, 0, 0, 0)

    def draw(self) -> None:
        if self.update():
            pygame.draw.rect(self.surface, self.color, self.rect)

    def move(self, dx: float, dy: float) -> None:
        self.position.x += dx
        self.position.y += dy

    def update(self) -> bool:
        """
        Updates the position and size of a rectangle on the screen according to the camera.
        Returns False if the object is outside the visible area of ​​the screen.
        """

        world_pos_px = pygame.Vector2(self.position) * self.base_cell_size_world
        world_size_px = pygame.Vector2(self.size) * self.base_cell_size_world

        screen_pos = self.cam.world_to_screen(world_pos_px)
        screen_size = pygame.Vector2(world_size_px) * self.cam.zoom

        # zaokrąglenie do intów (pygame.Rect wymaga int)
        rect_x = int(screen_pos.x)
        rect_y = int(screen_pos.y)
        rect_w = int(screen_size.x)
        rect_h = int(screen_size.y)

        self.rect.update(rect_x, rect_y, rect_w, rect_h)

        screen_w, screen_h = self.surface.get_size()
        visible = (
            self.rect.right >= 0
            and self.rect.left <= screen_w
            and self.rect.bottom >= 0
            and self.rect.top <= screen_h
        )

        return visible
