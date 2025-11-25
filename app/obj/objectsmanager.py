import math
from typing import Callable, List, Optional, Tuple, Union

import pygame
from Box2D import b2CircleShape, b2PolygonShape, b2Vec2, b2World
from obj.camera import Camera
from obj.guielements.stoper import Stoper
from obj.impulsecollector import ImpulseCollector
from obj.physicobject import Features

from .realobject import RealObject


class ObjectsManager:
    def __init__(
        self,
        surface: pygame.Surface,
        camera: Camera,
        cell_size: int,
        gravity: tuple[float, float] = (0.0, 9.8),
    ) -> None:
        self.world: b2World = b2World(gravity=gravity)
        self.surface: pygame.Surface = surface
        self.camera: Camera = camera
        self.cell_size: int = cell_size
        self.objects: list[RealObject] = []
        self.is_simulation_running: bool = False
        self.stop_simulation_at_collision: bool = False
        self.time_step: float = 1 / 100
        self.velocity_iterations: int = 8
        self.position_iterations: int = 3
        self.time: int = 0
        self.selected_obj: Optional[RealObject] = None
        self.selected_obj_is_being_dragged: bool = False
        self.stoper: Optional[Stoper] = None
        self.un_play: Optional[Callable[[], None]] = None
        self.collector = ImpulseCollector()
        self.world.contactListener = self.collector
        self.skip_force: bool = True
        self._time_ms_carry: int = 0

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
            impulse_collector=self.collector,
            features=features,
        )
        self.objects.append(new_object)

    def step_simulation(self) -> None:
        next_time = self.time + 10

        if self.stoper and self.stoper.value != 0:
            if next_time > self.stoper.value:
                remaining_ms = self.stoper.value - self.time
                final_dt = remaining_ms / 1000.0

                if final_dt > 0:
                    self._apply_forces()

                    self.world.Step(
                        final_dt,
                        self.velocity_iterations,
                        self.position_iterations,
                    )

                self.time = self.stoper.value
                self.is_simulation_running = False
                if self.un_play:
                    self.un_play()
                return

        if self.is_simulation_running:
            for obj in self.objects:
                obj.save_state_before_step()
            self._apply_forces()
            self.world.Step(
                self.time_step,
                self.velocity_iterations,
                self.position_iterations,
            )
            self.time += 10

        if self.collector.collision_detected and self.stop_simulation_at_collision:
            self.is_simulation_running = False
            self.collector.collision_detected = False
            if self.un_play:
                self.un_play()
            for obj in self.objects:
                obj.restore_state()
                obj.sync()
            self.skip_force = True
            self.time -= 10
            return

        self.collector.collision_detected = False

    def draw_objects(self) -> None:
        for obj in self.objects:
            obj.draw()

    def reset_simulation(self) -> None:
        self.remove_dust()
        for obj in self.objects:
            obj.reset()
        self.time = 0

    def run_simulation(self, run: bool) -> None:
        self.remove_dust()
        if run:
            for obj in self.objects:
                if obj.physics.body is None:
                    continue
                obj.physics.body.awake = True
            self.is_simulation_running = True
        else:
            self.is_simulation_running = False

    def select_object_at_position(
        self, position: Tuple[int, int]
    ) -> Optional[RealObject]:
        for obj in self.objects:
            if obj.is_point_inside(position):
                self.selected_obj = obj
                return obj
        if not self.selected_obj_is_being_dragged:
            self.selected_obj = None
        return None

    def end_dragging_obj(self):
        self.selected_obj_is_being_dragged = False
        self.selected_obj = None

    def move_selected_obj(self, vec: pygame.Vector2):
        obj = self.selected_obj
        if obj:
            obj.move(vec)
            if self.time == 0:
                obj.start_position = obj.physics.body.position.copy()
                obj.sync()

    def set_gravity_force(self, val: float = 0.0):
        self.world.gravity = b2Vec2(0.0, val)

    def remove_dust(self):
        def body_area(body):
            total_area = 0.0
            if body is None:
                return 0.0
            for fixture in body.fixtures:
                shape = fixture.shape
                if isinstance(shape, b2CircleShape):
                    total_area += math.pi * shape.radius**2
                elif isinstance(shape, b2PolygonShape):
                    verts = shape.vertices
                    total_area += 0.5 * abs(
                        sum(
                            x0 * y1 - x1 * y0
                            for (x0, y0), (x1, y1) in zip(verts, verts[1:] + verts[:1])
                        )
                    )
            return total_area

        for i, obj in enumerate(self.objects):
            if body_area(obj.physics.body) < 0.000004:
                self.objects[i].destroy()
                self.objects.pop(i)

    def _apply_forces(self):
        if self.skip_force:
            self.skip_force = False
            return
        for obj in self.objects:
            if obj.vector_manager:
                obj.vector_manager.forcemanager.apply_force()

    def transfer_to_json(self) -> dict:
        return {
            "cell_size": self.cell_size,
            "gravity": tuple(self.world.gravity),
            "objects": [obj.transfer_to_json() for obj in self.objects],
        }

    def load_from_json(self, data: dict) -> None:
        self.objects.clear()
        if data is None:
            return

        # -----------------------------
        # Wczytaj parametry managera
        # -----------------------------
        gravity = data.get("gravity")
        if isinstance(gravity, (list, tuple)) and len(gravity) > 1:
            g = gravity[1]
            self.set_gravity_force(round(g, 4))

        cell_size = data.get("cell_size")
        self.cell_size = int(cell_size) if isinstance(cell_size, (int, float)) else 100

        # -----------------------------
        # Wczytaj każdy obiekt
        # -----------------------------
        for obj_data in data.get("objects", []):
            # ---------- FEATURES ----------
            features_data = obj_data.get("features")
            if features_data is not None:
                features = Features(
                    linearVelocity=tuple(features_data["linearVelocity"]),
                    angularVelocity=features_data["angularVelocity"],
                    linearDamping=features_data["linearDamping"],
                    angularDamping=features_data["angularDamping"],
                    density=features_data["density"],
                    friction=features_data["friction"],
                    restitution=features_data["restitution"],
                    fixedRotation=features_data["fixedRotation"],
                    active=features_data["active"],
                )
            else:
                features = None

            # ---------- COLOR ----------
            c = obj_data["color"]
            color_vec = pygame.Vector3(c[0], c[1], c[2])

            # ---------- SIZE ----------
            size = obj_data["size"]
            if isinstance(size, list):
                if (
                    len(size) == 2
                    and isinstance(size[0], (float, int))
                    and isinstance(size[1], (float, int))
                ):
                    size = tuple(size)
                else:
                    size = [tuple(pt) for pt in size]

            # ---------- TWORZENIE OBIEKTU ----------
            self.add_object(
                obj_type=obj_data["obj_type"],
                shape_type=obj_data["shape_type"],
                size=size,
                position=tuple(obj_data["position"]),
                angle=obj_data["angle"],
                color=color_vec,
                features=features,
            )

            # ============================================================
            #  ODTWARZANIE DANYCH FIZYCZNYCH DLA OBIEKTÓW DYNAMICZNYCH
            # ============================================================
            if obj_data["obj_type"] != "static":
                body = self.objects[-1].physics.body

                # prędkości startowe
                lin_vel = obj_data.get("linear_velocity")
                if lin_vel:
                    body.linearVelocity = tuple(lin_vel)

                ang_vel = obj_data.get("angular_velocity")
                if ang_vel is not None:
                    body.angularVelocity = ang_vel

                # nadpisanie masy (jeśli ma sens — Box2D pozwala)
                try:
                    body.mass = obj_data["mass"]
                except AttributeError:
                    # masa jest readonly w Box2D – ignorujemy zmianę
                    pass

                # siła przyłożona
                if "applied_force" in obj_data:
                    fx, fy = obj_data["applied_force"]
                    self.objects[-1].vector_manager.forcemanager.applied_force = b2Vec2(
                        fx, fy
                    )

                # ============================================================
                #  ODTWARZANIE WIDOCZNOŚCI WEKTORÓW I TRAJEKTORII
                # ============================================================
                vis = obj_data

                obj = self.objects[-1]

                obj.trajectory.visible = vis.get("show_trajectory", False)
                obj.vector_manager.gravity_force.vector.visible = vis.get(
                    "show_gravity_force", False
                )
                obj.vector_manager.applied_force.vector.visible = vis.get(
                    "show_applied_force", False
                )
                obj.vector_manager.total_force.vector.visible = vis.get(
                    "show_total_force", False
                )

                obj.vector_manager.lineral_velocity.vector.visible = vis.get(
                    "show_velocity", False
                )
                obj.vector_manager.lineral_velocity.vec_x.visible = vis.get(
                    "show_velocity_x", False
                )
                obj.vector_manager.lineral_velocity.vec_y.visible = vis.get(
                    "show_velocity_y", False
                )
