from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Tuple, Union

import pygame  # type: ignore
from Box2D import b2World
from obj.camera import Camera
from obj.physicobject import Features

from .realobject import RealObject


class ObjectsManager:
    def __init__(
        self,
        surface: pygame.Surface,
        camera: Camera,
        cell_size: int,
        gravity: tuple[float, float] = (0.0, -9.8),
    ) -> None:
        self.world: b2World = b2World(gravity=gravity)
        self.surface: pygame.Surface = surface
        self.camera: Camera = camera
        self.cell_size: int = cell_size
        self.objects: list[RealObject] = []
        self.is_simulation_running: bool = False
        self.time_step: float = 1.0 / 60.0
        self.velocity_iterations: int = 8
        self.position_iterations: int = 3
        self.time: float = 0.00
        self.selected_obj: Optional[RealObject] = None
        self.selected_obj_is_being_dragged: bool = False

    def add_object(
        self,
        obj_type: str,
        shape_type: str,
        size: Union[Tuple[float, float], float, List[Tuple[float, float]]],
        position: Tuple[float, float],
        angle: float,
        color: pygame.Vector3,
        features: Optional[Features] = None,
    ) -> None:
        new_object = RealObject(
            world=self.world,
            surface=self.surface,
            camera=self.camera,
            obj_type=obj_type,
            shape_type=shape_type,
            size=size,
            position=position,
            angle=angle,
            color=color,
            cell_size=self.cell_size,
            features=features,
        )
        self.objects.append(new_object)

    def step_simulation(self) -> None:
        if self.is_simulation_running:
            self.world.Step(
                self.time_step,
                self.velocity_iterations,
                self.position_iterations,
            )
            self.time += self.time_step

    def draw_objects(self) -> None:
        # with ThreadPoolExecutor(max_workers=8) as executor:
        #     list(executor.map(lambda obj: obj.draw(), self.objects))
        for obj in self.objects:
            obj.draw()

    def reset_simulation(self) -> None:
        # with ThreadPoolExecutor(max_workers=8) as executor:
        #     list(executor.map(lambda obj: obj.reset(), self.objects))
        for obj in self.objects:
            obj.reset()
        self.time = 0.0

    def select_object_at_position(
        self, position: Tuple[int, int]
    ) -> Optional[RealObject]:
        for obj in self.objects:
            if obj.is_point_inside(position):
                self.selected_obj = obj
                return obj
        return None

    def end_dragging_obj(self):
        self.selected_obj_is_being_dragged = False
        self.selected_obj = None

    def move_selected_obj(self, vec: pygame.Vector2):
        obj = self.selected_obj
        if obj:
            obj.move(vec)
            if self.time == 0.00:
                obj.start_position = obj.physics.body.position.copy()
                obj.sync()
