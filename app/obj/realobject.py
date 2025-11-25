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
        self.obj_type = obj_type if shape_type != "point_particle" else 'dynamic'
        self.size = size
        self.start_angle = angle
        self.color = color
        self.cell_size = cell_size
        self.features = features

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
        self.vector_manager: VectorManager = VectorManager(self, impulse_collector)
        self.trajectory: Trajectory = Trajectory(
            camera,
            color,
            self.cell_size,
            self.physics.body,
            self.vector_manager.forcemanager,
        )

        body = self.physics.body
        self._prev_pos = body.position.copy()
        self._prev_angle = body.angle
        self._prev_linear_velocity = body.linearVelocity.copy()
        self._prev_angular_velocity = body.angularVelocity

        self.sync()

    def destroy(self):
        if self.physics and self.physics.body and self.physics.world:
            self.physics.world.DestroyBody(self.physics.body)
            self.physics.body = None

    # -------------------------------------------------------
    def sync(self) -> None:
        """
        Synchronizes visual position and rotation with the physics body.
        Converts Box2D world coordinates to visual world coordinates.
        """
        body = self.physics.body
        if body is None:
            return

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
        if self.trajectory:
            pos = pygame.Vector2(self.start_position.x, self.start_position.y)
            self.trajectory.draw_trajectory(pos)
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
        if self.trajectory:
            self.trajectory.clear_track()
        self.sync()

    def is_point_inside(self, position) -> bool:
        if not position or len(position) < 2:
            return False
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
        if self.trajectory:
            self.trajectory.clear_track()
        self.visual.object.move(vec)

    def transfer_to_json(self) -> Optional[dict]:
        if self.obj_type == 'static':
            return {
                "obj_type": self.obj_type,
                "shape_type": self.shape_type,
                "size": self.size,
                "position": [
                    float(self.start_position.x),
                    float(self.start_position.y),
                ],
                "angle": self.start_angle,
                "color": [self.color.x, self.color.y, self.color.z],
                "features": self.features.transfer_to_json() if self.features else None,
            }
        else:
            if self.vector_manager is None or self.trajectory is None:
                return None
            return {
                "obj_type": self.obj_type,
                "shape_type": self.shape_type,
                "size": self.size,
                "position": [
                    float(self.start_position.x),
                    float(self.start_position.y),
                ],
                "angle": self.start_angle,
                "color": [self.color.x, self.color.y, self.color.z],
                "features": self.features.transfer_to_json() if self.features else None,
                "mass": self.physics.body.mass,
                "linear_velocity": [
                    float(self.start_linearVelocity[0]),
                    float(self.start_linearVelocity[1]),
                ],
                "angular_velocity": self.start_angularVelocity,
                "applied_force": [
                    float(self.vector_manager.forcemanager.applied_force.x),
                    float(self.vector_manager.forcemanager.applied_force.y),
                ],
                "show_trajectory": self.trajectory.visible,
                "show_gravity_force": self.vector_manager.gravity_force.vector.visible,
                "show_applied_force": self.vector_manager.applied_force.vector.visible,
                "show_total_force": self.vector_manager.total_force.vector.visible,
                "show_velocity": self.vector_manager.lineral_velocity.vector.visible,
                "show_velocity_x": self.vector_manager.lineral_velocity.vec_x.visible,
                "show_velocity_y": self.vector_manager.lineral_velocity.vec_y.visible,
            }

    def save_state_before_step(self):
        body = self.physics.body
        self._prev_pos = body.position.copy()
        self._prev_angle = body.angle
        self._prev_linear_velocity = body.linearVelocity.copy()
        self._prev_angular_velocity = body.angularVelocity

    def restore_state(self):
        body = self.physics.body
        body.position = self._prev_pos
        body.angle = self._prev_angle
        body.linearVelocity = self._prev_linear_velocity
        body.angularVelocity = self._prev_angular_velocity
