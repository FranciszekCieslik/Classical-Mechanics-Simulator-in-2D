import math
from typing import Any, List, Optional, Tuple, Union

import pygame  # type: ignore
from Box2D import b2Vec2, b2World
from obj.camera import Camera
from obj.drawn.drawnobject import DrawnObject
from obj.impulsecollector import ImpulseCollector
from obj.physicobject import Features, PhysicObject
from obj.trajectory import Trajectory
from obj.vectormanager import VectorManager


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
        impulse_collector: ImpulseCollector,
        features: Optional[Features] = None,
    ) -> None:
        self.my_manager: Optional[Any] = None

        self.shape_type = shape_type
        self.cell_size = cell_size
        self.start_angle = angle

        self.start_linearVelocity = features.linearVelocity if features else (0.0, 0.0)
        self.start_angularVelocity = features.angularVelocity if features else 0.0

        self.physics = PhysicObject(
            obj_type=obj_type,
            shape_type=shape_type,
            size=size,
            position=position,
            angle=angle,
            world=world,
            features=features,
        )

        self.start_position = self.physics.body.position.copy()

        wc = self.physics.body.worldCenter
        bp = self.physics.body.position
        self.center_offset = b2Vec2(wc.x - bp.x, wc.y - bp.y)

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
        self.trayectory: Optional[Trajectory] = None
        self.vector_manager: Optional[VectorManager] = None
        if obj_type != 'static':
            self.trayectory = Trajectory(
                camera, color, self.cell_size, self.physics.body
            )
            self.vector_manager = VectorManager(self, impulse_collector)
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
        if self.vector_manager:
            self.vector_manager.update()

    # -------------------------------------------------------
    def draw(self) -> None:
        self.sync()
        self.visual.draw()
        if self.trayectory:
            pos = pygame.Vector2(self.start_position.x, self.start_position.y)
            self.trayectory.draw_trajectory(pos)
        if self.vector_manager:
            self.vector_manager.draw()

    # -------------------------------------------------------
    def reset(self) -> None:
        """Resets the object to its initial position and angle."""
        body = self.physics.body
        body.position = self.start_position
        body.angle = self.start_angle
        body.linearVelocity = self.start_linearVelocity
        body.angularVelocity = self.start_angularVelocity
        body.awake = True
        if self.trayectory:
            self.trayectory.clear_track()
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

    def move(self, vec: pygame.Vector2) -> None:
        """
        Moves the object by a given vector (in screen pixels).
        Automatically converts to world coordinates using self.cell_size.
        Keeps both physics (Box2D) and visual (Pygame) states synchronized.
        """
        if vec.length_squared() == 0:
            return

        zoom = getattr(self.visual.camera, "zoom", 1.0)
        world_vec = vec / (self.cell_size * zoom)

        body = self.physics.body

        new_pos = body.position - (world_vec.x, world_vec.y)
        body.position = new_pos

        if not self.physics.is_static:
            body.awake = True
        if self.trayectory:
            self.trayectory.clear_track()
        self.visual.object.move(vec)
