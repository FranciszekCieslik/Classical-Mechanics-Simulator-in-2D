from typing import List, Optional, Tuple, Union

import pygame  # type: ignore
from Box2D import b2World
from obj.camera import Camera
from obj.drawn.drawnobject import DrawnObject
from obj.physicobject import Features, PhysicObject


class RealObject:
    """
    Integrates PhysicObject (Box2D physics) and DrawnObject (Pygame rendering).
    Synchronizes world position and rotation from physics simulation to visual representation.
    """

    def __init__(
        self,
        world: b2World,
        surface: pygame.Surface,
        camera: Camera,
        type: str,
        shape: str,
        size: Union[Tuple[float, float], float, List[Tuple[float, float]]],
        position: Tuple[float, float],
        angle: float,
        color: pygame.Vector3,
        cell_size: int,
        features: Optional[Features] = None,
    ) -> None:
        """
        Creates a new RealObject that links physical and visual components.

        Args:
            world: Box2D world instance
            surface: pygame.Surface — rendering target
            camera: Camera object
            type: 'static' or 'dynamic'
            shape: 'rectangle', 'circle', or 'triangle'
            size: geometric shape definition
            position: (x, y) position in Box2D world (meters)
            angle: initial rotation (radians)
            color: RGB color (0–255)
            cell_size: scaling factor between physics world units and visual world
            features: optional physics parameters
        """
        # physics setup
        self.physics = PhysicObject(
            type=type,
            shape=shape,
            size=size,
            position=position,
            angle=angle,
            world=world,
            features=features,
        )

        # drawing setup
        # convert Box2D position → pygame.Vector2 for drawn object
        pygame_position = pygame.Vector2(position[0], position[1])

        if shape == "rectangle":
            pygame_size = pygame.Vector2(size)
        else:
            pygame_size = size

        self.visual = DrawnObject(
            shape=shape,
            size=pygame_size,
            position=pygame_position,
            color=color,
            surface=surface,
            camera=camera,
            cell_size=cell_size,
        )

        self.cell_size = cell_size
        self.shape = shape

    # -------------------------------------------------------
    def sync(self) -> None:
        """
        Synchronizes visual position and rotation with the physics body.
        Converts Box2D world coordinates to visual world coordinates.
        """
        body = self.physics.body
        pos = body.position
        angle = body.angle

        # Box2D units (usually meters) → world units (e.g. tiles)
        self.visual.object.position = pygame.Vector2(pos.x, pos.y)
        self.visual.object.angle = (
            angle if hasattr(self.visual.object, "angle") else 0.0
        )

    # -------------------------------------------------------
    def draw(self) -> None:
        """
        Updates synchronization and draws the object to the screen.
        """
        self.sync()
        self.visual.update()
        self.visual.draw()

    # -------------------------------------------------------
    def apply_force(self, force: Tuple[float, float]) -> None:
        """
        Applies a force to the physics body (if dynamic).
        """
        self.physics.apply_force(force)

    # -------------------------------------------------------
    def set_mass(self, mass: float) -> None:
        """
        Sets the mass of the physics body.
        """
        self.physics.set_body_mass(mass)
