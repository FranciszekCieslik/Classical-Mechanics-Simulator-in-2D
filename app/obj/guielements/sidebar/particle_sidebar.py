from typing import Any, Optional, Union

import pygame
import thorpy as tp
from Box2D import b2PolygonShape, b2Vec2
from obj.guielements.numberinput import NumberInput
from obj.guielements.sidebar.featurespanel import FeaturesPanel
from obj.guielements.sidebar.selectortype import SelectorType
from obj.guielements.sidebar.sidesize import SideSize
from obj.objectsmanager import ObjectsManager
from obj.physicobject import Features
from obj.realobject import RealObject


def safe_float(value, default=0.0) -> float:
    try:
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)
        value_str = str(value).strip()
        return float(value_str) if value_str else default
    except (ValueError, TypeError):
        return default


class PointParticleSideBar:
    def __init__(self, objectmanager: ObjectsManager) -> None:
        self.objectmanager = objectmanager
        self.screen: pygame.Surface = pygame.display.get_surface()
        self.visible: bool = False
        self.speed: int = 12
        self.obj: Optional[RealObject] = None
        self.top_margin: int = 15
        self.width: int = 365
        self.height: int = 165
        self.offset: int = self.width

        # --- Thorpy Elements ---
        ico_path = "app/assets/icons/x-square.svg"
        img = pygame.image.load(ico_path)
        img = pygame.transform.smoothscale(img, (30, 30))
        variant = tp.graphics.change_color_on_img(
            img, img.get_at((0, 0)), (100, 100, 100)
        )
        xbtn = tp.ImageButton("", img.copy(), img_hover=variant)
        xbtn.at_unclick = self.hide
        # --- Build Btn ---
        ico_path = "app/assets/icons/build.svg"
        img = pygame.image.load(ico_path)
        img = pygame.transform.smoothscale(img, (30, 30))
        variant = tp.graphics.change_color_on_img(
            img, img.get_at((0, 0)), (100, 100, 100)
        )
        build_btn = tp.ImageButton("", img.copy(), img_hover=variant)
        build_btn.at_unclick = self.apply
        helper = tp.Helper("Apply\nchanges", build_btn, countdown=30, offset=(80, 0))
        helper.set_font_size(12)
        # --- Title ---
        titlegroup = tp.Group(
            elements=[xbtn, tp.Text("Poin Particle Controls", font_size=18), build_btn],
            mode="h",
            margins=(0, 0),
            gap=15,
        )

        # --- Position ---
        self.x_pos = NumberInput("", placeholder="00.000")
        self.y_pos = NumberInput("", placeholder="00.000")
        self.y_pos.max_length = 5
        self.x_pos.max_length = 5
        self.pos_group = tp.Group(
            [
                tp.Text("X:", font_size=14),
                self.x_pos,
                tp.Text("Y:", font_size=14),
                self.y_pos,
            ],
            "h",
        )
        # --- Fixtures ---
        self.mass: NumberInput
        self.start_velocity_x: NumberInput
        self.start_velocity_y: NumberInput
        self.curr_velocity_x: NumberInput
        self.curr_velocity_y: NumberInput
        self.applied_force_x: NumberInput
        self.applied_force_y: NumberInput

        # lista nazw wszystkich pól tekstowych
        fields = [
            "mass",
            "start_velocity_x",
            "start_velocity_y",
            "curr_velocity_x",
            "curr_velocity_y",
            "applied_force_x",
            "applied_force_y",
        ]

        # automatyczna inicjalizacja
        for name in fields:
            text_input = NumberInput("", placeholder="00.00")
            if not "velocity" in name and not "force" in name:
                text_input.set_only_non_negative()
            text_input.max_length = 5
            setattr(self, name, text_input)

        self.show_trajectory = tp.Checkbox()
        self.show_lineral_velocity = tp.Checkbox()
        self.show_lineral_v_comp = tp.Checkbox()
        self.show_applied_force = tp.Checkbox()
        self.show_gravity_force = tp.Checkbox()
        self.show_resultant_force = tp.Checkbox()

        # --- main group ---
        self.main_group = tp.Group(
            elements=[
                titlegroup,
                tp.Line('h', 360),
                self.pos_group,
                tp.Line("h", 360),
                tp.Group(
                    [
                        tp.Text("Show trajectory", font_size=14),
                        self.show_trajectory,
                        tp.Group(
                            [
                                tp.Group(
                                    [
                                        tp.Text(
                                            'Show lineral velocity vector', font_size=14
                                        ),
                                        self.show_lineral_velocity,
                                    ],
                                    'h',
                                ),
                                tp.Group(
                                    [
                                        tp.Text('Show components', font_size=14),
                                        self.show_lineral_v_comp,
                                    ],
                                    'h',
                                ),
                            ],
                            'v',
                            align='right',
                        ),
                    ],
                    "h",
                ),
                tp.Line("h", 360),
                tp.Group(
                    [
                        tp.Group(
                            [tp.Text("Mass:", font_size=14), self.mass],
                            "h",
                        ),
                    ],
                    "v",
                    align='right',
                ),
                tp.Line("h", 360),
                tp.Text("Lineral Velocity", font_size=16),
                tp.Line("h", 360),
                tp.Group(
                    [
                        tp.Group(
                            [
                                tp.Text("Start:", font_size=14),
                                tp.Text("x:", font_size=14),
                                self.start_velocity_x,
                                tp.Text("y:", font_size=14),
                                self.start_velocity_y,
                            ],
                            "h",
                        ),
                        tp.Group(
                            [
                                tp.Text("Current", font_size=14),
                                tp.Text("x:", font_size=14),
                                self.curr_velocity_x,
                                tp.Text("y:", font_size=14),
                                self.curr_velocity_y,
                            ],
                            "h",
                        ),
                    ],
                    'v',
                    align='right',
                ),
                tp.Line("h", 360),
                tp.Text("Additional Force", font_size=16),
                tp.Line("h", 360),
                tp.Group(
                    [
                        tp.Text('x:', font_size=14),
                        self.applied_force_x,
                        tp.Text('y:', font_size=14),
                        self.applied_force_y,
                    ],
                    'h',
                ),
                tp.Line("h", 360),
                tp.Group(
                    [
                        tp.Group(
                            [
                                tp.Group(
                                    [
                                        tp.Text("Show applied force", font_size=14),
                                        self.show_applied_force,
                                    ],
                                    "h",
                                ),
                                tp.Group(
                                    [
                                        tp.Text("Show gravity force", font_size=14),
                                        self.show_gravity_force,
                                    ],
                                    "h",
                                ),
                            ],
                            'h',
                        ),
                        tp.Group(
                            [
                                tp.Text("Show resutant force", font_size=14),
                                self.show_resultant_force,
                            ],
                            "h",
                        ),
                    ],
                    'v',
                    align='right',
                ),
            ],
            margins=(0, 0),
        )

        self.box = tp.Box([self.main_group])
        self.box.set_topleft(self.screen.get_width() + self.width, self.top_margin)
        self.box.set_size((self.width, self.box.rect.height))
        self.box.set_bck_color((0, 0, 0))

        self.container = tp.Group(
            [self.box],
            mode=None,
        )

    def show(self) -> None:
        if self.visible:
            self.hide()
            self.update()
            return
        self.visible = True

    def hide(self) -> None:
        self.obj = None
        self.visible = False
        self.reset_inputs()

    def update(self) -> None:
        target_offset = 0 if self.visible else self.screen.get_width()
        if abs(self.offset - target_offset) > 1:
            self.offset += int((target_offset - self.offset) / self.speed)
        else:
            self.offset = target_offset
        x = self.screen.get_width() - self.width + int(self.offset)
        self.box.set_topleft(x, self.top_margin)

    def get_data_from_real_obj(self, rlobjct: RealObject) -> None:
        self.obj = rlobjct
        body = self.obj.physics.body
        pos = body.position
        self.x_pos.value = str(round(pos.x, 3))
        correct_y = -round(pos.y, 3) if pos.y != 0 else 0.00
        self.y_pos.value = str(correct_y)

        self.mass.value = str(round(body.mass, 3))
        self.start_velocity_x.value = str(round(self.obj.start_linearVelocity[0], 3))
        vy = (
            -1 * round(self.obj.start_linearVelocity[1], 3)
            if round(self.obj.start_linearVelocity[1], 3) != 0
            else 00.00
        )
        self.start_velocity_y.value = str(vy)
        self.curr_velocity_x.value = str(round(body.linearVelocity.x, 3))
        vy = (
            -1 * round(body.linearVelocity.y, 3)
            if round(body.linearVelocity.y, 3) != 0
            else 00.00
        )
        self.curr_velocity_y.value = str(vy)

        if rlobjct.trajectory and rlobjct.vector_manager:
            self.show_trajectory.value = rlobjct.trajectory.visible
            lv = rlobjct.vector_manager.lineral_velocity
            self.show_lineral_velocity.value = lv.vector.visible
            self.show_lineral_v_comp.value = lv.vec_x.visible
            self.show_gravity_force.value = (
                rlobjct.vector_manager.gravity_force.vector.visible
            )
            self.show_applied_force.value = (
                rlobjct.vector_manager.applied_force.vector.visible
            )
            self.show_resultant_force.value = (
                rlobjct.vector_manager.total_force.vector.visible
            )
            af = rlobjct.vector_manager.forcemanager.applied_force
            self.applied_force_x.value = str(round(af.x, 3))
            self.applied_force_y.value = str(round(-1 * af.y, 3))

    def apply_to_real_obj(self, rlobjct: RealObject) -> Optional[RealObject]:

        if self.obj is None:
            return None

        world = rlobjct.physics.world
        surface = rlobjct.visual.surface
        camera = rlobjct.visual.camera
        shape_type = self.obj.shape_type
        position = (safe_float(self.x_pos.value), -1 * safe_float(self.y_pos.value))
        color = rlobjct.visual.color
        cell_size = rlobjct.cell_size
        obj_type = 'dynamic'
        features = None

        start_linearVelocity = (
            safe_float(self.start_velocity_x.value),
            -1 * safe_float(self.start_velocity_y.value),
        )

        lv = (
            safe_float(self.curr_velocity_x.value),
            -1 * safe_float(self.curr_velocity_y.value),
        )
        mass = safe_float(self.mass.value, 1.0)

        features = Features(linearVelocity=lv)

        angle = 0.0
        size = 10.0
        new_obj = RealObject(
            world,
            surface,
            camera,
            obj_type,
            shape_type,
            size,
            position,
            angle,
            color,
            cell_size,
            self.objectmanager.collector,
            features,
        )

        if mass != 0:
            new_obj.physics.body.fixtures[0].density = new_obj.physics.body.fixtures[
                0
            ].density * (mass / new_obj.physics.body.mass)
            new_obj.physics.body.mass = mass
            new_obj.physics.body.ResetMassData()
        new_obj.start_linearVelocity = start_linearVelocity
        if self.show_trajectory.value:
            if new_obj.trajectory:
                new_obj.trajectory.visible = True
        if new_obj.vector_manager:
            if self.show_lineral_velocity.value:
                new_obj.vector_manager.lineral_velocity.show_vector()
            if self.show_lineral_v_comp.value:
                new_obj.vector_manager.lineral_velocity.show_components()
            if self.show_applied_force.value:
                new_obj.vector_manager.applied_force.show_vector()
            if self.show_gravity_force.value:
                new_obj.vector_manager.gravity_force.show_vector()
            if self.show_resultant_force.value:
                new_obj.vector_manager.total_force.show_vector()
            x = safe_float(self.applied_force_x.value)
            y = -1 * safe_float(self.applied_force_y.value)
            new_obj.vector_manager.forcemanager.applied_force = b2Vec2(x, y)

        return new_obj

    def apply(self):
        if self.obj:
            new_obj = self.apply_to_real_obj(self.obj)
            if new_obj:
                for i, old_obj in enumerate(self.objectmanager.objects):
                    if old_obj == self.obj:
                        self.objectmanager.objects[i] = new_obj
                        break
        self.hide()

    def reset_inputs(self) -> None:
        self.mass.value = ""

        self.start_velocity_x.value = ""
        self.start_velocity_y.value = ""
        self.curr_velocity_x.value = ""
        self.curr_velocity_y.value = ""

        self.applied_force_x.value = ""
        self.applied_force_y.value = ""

        self.show_trajectory.value = False
        self.show_lineral_velocity.value = False
        self.show_lineral_v_comp.value = False
        self.show_applied_force.value = False
        self.show_gravity_force.value = False
        self.show_resultant_force.value = False
