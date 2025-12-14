from typing import Any

from Box2D import b2Vec2
from obj.impulsecollector import ImpulseCollector


class ForceManager:
    def __init__(
        self, body: Any, impulse_collector: ImpulseCollector, dt: float = 1 / 200
    ):
        self.body = body
        self.dt = dt
        self.prev_velocity = body.linearVelocity

        self.collector = impulse_collector

        g = self.body.world.gravity
        self.gravity_force = g * self.body.mass
        self.applied_force = b2Vec2(0, 0)
        self.total_force = b2Vec2(0, 0)
        self.net_force = b2Vec2(0, 0)

    def update(self):
        dt = self.dt
        g = self.body.world.gravity
        self.gravity_force = g * self.body.mass

        contact_list = self.collector.impulses.pop(self.body, [])
        F_contact = sum(contact_list, b2Vec2(0, 0)) * (1.0 / dt)

        continuous_force = self.applied_force + self.gravity_force

        tf = continuous_force + F_contact
        self.total_force = b2Vec2(round(tf.x, 3), round(tf.y, 3))

    def apply_force(self):
        if self.applied_force != (0, 0) and self.body.awake:
            self.body.ApplyForceToCenter(self.applied_force, True)
