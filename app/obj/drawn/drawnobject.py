import typing
from typing import Tuple, Union

import pygame  # type: ignore
from obj.camera import Camera
from obj.drawn.circle import Circle
from obj.drawn.empty import Empty
from obj.drawn.pointparticle import PointParticle
from obj.drawn.rectangle import Rectangle
from obj.drawn.triangle import Triangle

DrawnShape = Union[Circle, Triangle, Rectangle, PointParticle]


class DrawnObject:
    """
    Wrapper class that manages drawable shapes (Rectangle, Circle, Triangle)
    and delegates draw, move, and update calls to the correct implementation.
    """

    def __init__(
        self,
        shape: str,
        size: typing.Any,
        position: pygame.Vector2,
        color: pygame.Vector3,
        surface: pygame.Surface,
        camera: Camera,
        cell_size: int,
    ) -> None:
        """
        Initializes a drawable object based on its shape type.

        Args:
            shape: Shape type ('rectangle', 'circle', 'triangle', 'point_particle')
            size: Shape size — depends on type:
                rectangle -> pygame.Vector2(width, height)
                circle -> float (radius)
                triangle -> list[pygame.Vector2, pygame.Vector2, pygame.Vector2]
            position: World position of the shape
            color: RGB color (0–255)
            surface: Pygame surface to draw on
            camera: Camera object (for world→screen transformations)
            cell_size: Scaling factor between world and screen
        """

        self.shape = shape.lower()
        self.surface = surface
        self.camera = camera
        self.color = color
        self.position = position
        self.size = size
        self.cell_size = cell_size
        self.object: DrawnShape | Empty = Empty()

        if self.shape == "rectangle":
            self.object = Rectangle(surface, camera, position, color, size, cell_size)
        elif self.shape == "circle":
            self.object = Circle(surface, camera, position, color, size, cell_size)
        elif self.shape == "triangle":
            self.object = Triangle(surface, camera, position, color, size, cell_size)
        elif self.shape == "point_particle":
            self.object = PointParticle(surface, camera, position, color, cell_size)
        else:
            raise ValueError(f"Unsupported shape type: {shape}")

    # ----------------------------------------------
    def draw(self) -> None:
        """Draws the underlying shape."""
        self.object.draw()

    def move(self, vec: pygame.Vector2) -> None:
        """Moves the shape in world coordinates."""
        self.object.move(vec)

    # ----------------------------------------------
    def update(self) -> bool:
        """Updates shape position and returns visibility flag."""
        return self.object.update()

    def set_position(self, position: pygame.Vector2) -> None:
        """Sets the absolute position of the shape in world coordinates."""
        if hasattr(self.object, "set_position"):
            self.object.set_position(position)

    def set_angle(self, angle: float) -> None:
        """Sets the absolute rotation angle (in degrees) if supported."""
        if hasattr(self.object, "set_angle"):
            self.object.set_angle(angle)

    def is_point_inside(self, point: Tuple[int, int]) -> bool:
        """Checks if a given point (in screen coordinates) is inside the shape."""
        if hasattr(self.object, "is_point_inside"):
            return self.object.is_point_inside(point)
        return False
