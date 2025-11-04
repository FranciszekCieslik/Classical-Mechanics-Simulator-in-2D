from typing import Optional

import pygame
from obj.camera import Camera


class Empty:
    def __init__(
        self,
        surface: Optional[pygame.Surface] = None,
        cam: Optional[Camera] = None,
        position: Optional[pygame.Vector2] = None,
        color: Optional[pygame.Vector3] = None,
        size: Optional[pygame.Vector2] = None,
        cell_size: Optional[int] = None,
        angle: Optional[float] = None,
    ) -> None:
        """
        Empty shape that does nothing.
        """
        self.angle = angle
        self.position = position
        self.color = color
        self.size = size
        self.cell_size = cell_size
        self.surface = surface
        self.cam = cam

    # ------------------------------------------------------
    def draw(self) -> None:
        return

    def update(self) -> bool:
        return False

    # ------------------------------------------------------
    def move(self, vec: pygame.Vector2) -> None:
        return

    def rotate(self, da: float) -> None:
        return

    def set_position(self, position: pygame.Vector2) -> None:
        return

    def set_angle(self, angle: float) -> None:
        return
