import math
from typing import List, Optional, Tuple, Union

import pygame  # type: ignore
from Box2D import b2Vec2, b2World
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
        obj_type: str,
        shape_type: str,
        size: Union[Tuple[float, float], float, List[Tuple[float, float]]],
        position: Tuple[float, float],
        angle: float,
        color: pygame.Vector3,
        cell_size: int,
        features: Optional[Features] = None,
    ) -> None:

        self.shape_type = shape_type
        self.cell_size = cell_size
        self.start_angle = angle

        # --- 1️⃣ Inicjalizacja fizyki ---
        self.physics = PhysicObject(
            obj_type=obj_type,
            shape_type=shape_type,
            size=size,
            position=position,
            angle=angle,
            world=world,
            features=features,
        )

        # Pozycja startowa (anchor, NIE centroid)
        self.start_position = self.physics.body.position.copy()

        # 🔹 Obliczamy offset między środkiem masy a punktem anchor
        wc = self.physics.body.worldCenter
        bp = self.physics.body.position
        self.center_offset = b2Vec2(wc.x - bp.x, wc.y - bp.y)

        # --- 2️⃣ Inicjalizacja wizualna ---
        pygame_position = pygame.Vector2(position)
        if shape_type == "rectangle":
            pygame_size = pygame.Vector2(size)
        else:
            pygame_size = size

        self.visual = DrawnObject(
            shape=shape_type,
            size=pygame_size,
            position=pygame_position,
            color=color,
            surface=surface,
            camera=camera,
            cell_size=cell_size,
        )

        self.sync()

    # -------------------------------------------------------
    def sync(self) -> None:
        """
        Synchronizes visual position and rotation with the physics body.
        Converts Box2D world coordinates to visual world coordinates.
        """
        body = self.physics.body
        pos = pygame.Vector2(body.position.x, body.position.y)
        angle = math.degrees(body.angle)

        self.visual.object.set_position(pos)
        self.visual.object.set_angle(angle)

    # -------------------------------------------------------
    def draw(self) -> None:
        self.sync()
        self.visual.draw()

    # -------------------------------------------------------
    def reset(self) -> None:
        """Resets the object to its initial position and angle."""
        body = self.physics.body
        body.position = self.start_position
        body.angle = self.start_angle
        body.linearVelocity = (0, 0)
        body.angularVelocity = 0
        body.awake = True  # <- bez tego ciało pozostaje „uśpione”

        self.sync()

    def is_point_inside(self, position) -> bool:
        """
        Checks if a given point (in pixels) is inside the drawn object.
        """
        return self.visual.is_point_inside(position)

    def get_self_if_point_inside(self, position) -> Optional["RealObject"]:
        """
        Returns self if the given point (in pixels) is inside the drawn object, else None.
        """
        if self.visual.is_point_inside(position):
            return self
        return None
