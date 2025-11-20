import math
from typing import Optional

import pygame
import thorpy as tp
from Box2D import b2Vec2
from obj.camera import Camera
from obj.objectsmanager import ObjectsManager
from obj.realobject import RealObject
from pygame import Vector2, display


def vector_to_scalar(vec: b2Vec2 | Vector2):
    x, y = vec.x, vec.y
    scalar = x * x + y * y
    return math.sqrt(scalar)


class PopInfo:
    def __init__(
        self, camera: Camera, objectsmanager: ObjectsManager, cell_size: int = 100
    ):
        self.pos = Vector2(0, 0)
        self.offset = Vector2(10, -10)

        self.cooldown = 15 * 60
        self.time_left = self.cooldown

        self.tp_text = tp.Text("Object", font_size=12)
        self.box = tp.Box([self.tp_text])

        self.cell_size = cell_size
        self.camera = camera
        self.objectsmanager = objectsmanager
        self.selected_obj: Optional[RealObject] = None

        self.hide()

    def _text_gen(self, rlobj: RealObject):
        if rlobj.obj_type == 'static':
            return 'Static object'

        body = rlobj.physics.body
        pos = body.position
        lv = vector_to_scalar(body.linearVelocity)
        av = body.fixtures[0].body.angularVelocity
        acc = (
            vector_to_scalar(rlobj.vector_manager.forcemanager.total_force) / body.mass
        )
        ek = 0.5 * body.mass * lv * lv
        dep = body.mass * vector_to_scalar(body.world.gravity) * -1 * pos.y
        I = body.inertia
        er = 0.5 * I * av * av
        return (
            f"Object at position: ({pos.x:.2f}, {-pos.y:.2f}) m\n"
            f"Linear velocity: {lv:.3f} m/s\n"
            f"Acceleration: {acc:.3f} m/s²\n"
            f"Angular velocity: {av:.3f} rad/s\n"
            f"Kinetic energy: {ek:.3f} J\n"
            f"Rotational energy: {er:.3f} J\n"
            f"Potential energy: {dep:.3f} J\n"
        )

    def _position(self):
        if not self.selected_obj:
            return

        body = self.selected_obj.physics.body
        if not body:
            self.hide()
            return
        world_pos = Vector2(body.position.x, body.position.y)

        screen_pos = self.camera.world_to_screen(world_pos * self.cell_size)
        self.pos = screen_pos

    def update(self, rlobj: Optional[RealObject]):
        """Wywoływane, gdy użytkownik wybiera obiekt."""
        if rlobj is None:
            return

        self.selected_obj = rlobj
        self.time_left = self.cooldown

        self._position()
        self.tp_text.set_text(self._text_gen(rlobj))

    def tick(self):
        """Wywoływane co klatkę — aktualizacja pozycji, danych i wygaszanie."""
        if self.time_left <= 0:
            self.hide()
            return

        self.time_left -= 1
        if len(self.objectsmanager.objects) > 0:
            if not self.selected_obj in self.objectsmanager.objects:
                self.selected_obj = self.objectsmanager.objects[-1]
                self.time_left = self.cooldown

        self._position()

        if self.selected_obj:
            self.tp_text.set_text(self._text_gen(self.selected_obj))

        final = self.pos + self.offset
        self.box.set_topleft(final.x, final.y)

    def get(self):
        return self.box

    def hide(self):
        x, y = pygame.display.get_window_size()
        self.box.set_topleft(x, y)
