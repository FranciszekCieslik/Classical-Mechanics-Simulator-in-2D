import math
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
        obj_type: str,
        shape_type: str,
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
            shape_type: 'rectangle', 'circle', or 'triangle'
            size: geometric shape definition
            position: (x, y) position in Box2D world (meters)
            angle: initial rotation (radians)
            color: RGB color (0–255)
            cell_size: scaling factor between physics world units and visual world
            features: optional physics parameters
        """
        self.start_position = position
        self.start_angle = angle

        # physics setup
        self.physics = PhysicObject(
            obj_type=obj_type,
            shape_type=shape_type,
            size=size,
            position=position,
            angle=angle,
            world=world,
            features=features,
        )

        # drawing setup
        # convert Box2D position → pygame.Vector2 for drawn object
        pygame_position = pygame.Vector2(position[0], position[1])

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

        self.cell_size = cell_size
        self.shape_type = shape_type

    # -------------------------------------------------------
    def sync(self) -> None:
        """
        Synchronizes visual position and rotation with the physics body.
        Converts Box2D world coordinates to visual world coordinates.
        """
        body = self.physics.body
        pos = body.worldCenter
        angle = body.angle

        # Domyślnie synchronizujemy ze środkiem masy (centroid)
        corrected_pos = pygame.Vector2(pos.x, pos.y)

        # Dla trójkąta — korekta pozycji, żeby dolny wierzchołek był tam, gdzie w fizyce
        if self.shape_type == "triangle":
            vertices = [v for v in self.physics.fixture.shape.vertices]
            # centroid w lokalnych współrzędnych (0,0)
            centroid_y = sum(v[1] for v in vertices) / 3.0
            min_y = min(v[1] for v in vertices)
            offset_y = centroid_y - min_y

            # Korekta pozycji w dół o offset_y (po transformacji przez kąt obrotu)
            sin_a = math.sin(angle)
            cos_a = math.cos(angle)
            dx, dy = 0, -offset_y  # przesunięcie lokalne w dół
            # obracamy wektor przesunięcia zgodnie z kątem ciała
            rotated_offset = pygame.Vector2(
                dx * cos_a - dy * sin_a,
                dx * sin_a + dy * cos_a,
            )
            corrected_pos += rotated_offset
            # --- Korekta dla kół ---

        # Synchronizuj pozycję i obrót rysowanego obiektu
        self.visual.object.set_position(corrected_pos)
        self.visual.object.set_angle(math.degrees(angle))

    # -------------------------------------------------------
    def draw(self) -> None:
        """
        Updates synchronization and draws the object to the screen.
        """
        self.sync()
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
