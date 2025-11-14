from typing import Any

from Box2D import b2Vec2
from obj.drawn.vectorcomponents import VectorComponents
from pygame import Color, Vector3


class VectorManager:
    def __init__(self, obj: Any):
        self.obj = obj.physics.body
        self.lineral_velocity = VectorComponents(
            b2Vec2(self.obj.worldCenter),
            b2Vec2(self.obj.linearVelocity),
            Color(Vector3([max(c - 100, 20) for c in obj.visual.color[:3]])),
            obj.visual.camera,
            obj.visual.cell_size,
        )
        self.lineral_velocity.set_components_color(Color(0, 0, 0))

    def update(self):
        self.lineral_velocity.update(
            b2Vec2(self.obj.worldCenter), b2Vec2(self.obj.linearVelocity)
        )

    def draw(self):
        self.lineral_velocity.draw()
