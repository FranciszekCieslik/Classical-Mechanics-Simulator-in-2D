from typing import Any

from Box2D import b2Vec2
from obj.drawn.vectorcomponents import VectorComponents
from obj.forcemanager import ForceManager
from obj.impulsecollector import ImpulseCollector
from pygame import Color, Vector3


class VectorManager:
    def __init__(self, obj: Any, impulse_collector: ImpulseCollector):
        self.obj = obj.physics.body
        self.lineral_velocity = VectorComponents(
            b2Vec2(self.obj.worldCenter),
            b2Vec2(self.obj.linearVelocity),
            Color(Vector3([max(c - 100, 20) for c in obj.visual.color[:3]])),
            obj.visual.camera,
            obj.visual.cell_size,
        )
        self.lineral_velocity.set_unit("m/s")
        self.lineral_velocity.set_components_color(Color(0, 0, 0))
        self.forcemanager = ForceManager(self.obj, impulse_collector)

        self.gravity_force = VectorComponents(
            b2Vec2(self.obj.worldCenter),
            b2Vec2(self.forcemanager.gravity_force),
            Color(255, 0, 0),
            obj.visual.camera,
            obj.visual.cell_size,
        )
        self.gravity_force.set_unit("N")
        self.applied_force = VectorComponents(
            b2Vec2(self.obj.worldCenter),
            b2Vec2(self.forcemanager.applied_force),
            Color(0, 0, 255),
            obj.visual.camera,
            obj.visual.cell_size,
        )
        self.applied_force.set_unit("N")
        self.total_force = VectorComponents(
            b2Vec2(self.obj.worldCenter),
            b2Vec2(self.forcemanager.total_force),
            Color(Vector3([max(c - 100, 20) for c in obj.visual.color[:3]])),
            obj.visual.camera,
            obj.visual.cell_size,
        )
        self.total_force.set_unit("N")

    def update(self):
        self.lineral_velocity.update(
            b2Vec2(self.obj.worldCenter), b2Vec2(self.obj.linearVelocity)
        )
        self.forcemanager.update()
        self.gravity_force.update(
            b2Vec2(self.obj.worldCenter), b2Vec2(self.forcemanager.gravity_force)
        )
        self.total_force.update(
            b2Vec2(self.obj.worldCenter), b2Vec2(self.forcemanager.total_force)
        )
        self.applied_force.update(
            b2Vec2(self.obj.worldCenter), b2Vec2(self.forcemanager.applied_force)
        )

    def draw(self):
        self.lineral_velocity.draw()
        self.gravity_force.draw()
        self.applied_force.draw()
        self.total_force.draw()

    def scale(self, factor: float):
        self.lineral_velocity.scale(factor)
        self.gravity_force.scale(factor)
        self.applied_force.scale(factor)
        self.total_force.scale(factor)

    def scale_forces(self, factor: float):
        self.gravity_force.scale(factor)
        self.applied_force.scale(factor)
        self.total_force.scale(factor)

    def scale_velocity(self, factor: float):
        self.lineral_velocity.scale(factor)
