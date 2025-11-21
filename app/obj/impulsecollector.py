from typing import Callable, Optional

from Box2D import b2ContactListener, b2Vec2


class ImpulseCollector(b2ContactListener):
    def __init__(self):
        super().__init__()
        self.impulses = {}  # body -> dict with normal/tangent
        self.function: Optional[Callable[[], None]] = None

    def PostSolve(self, contact, impulse):
        bodyA = contact.fixtureA.body
        bodyB = contact.fixtureB.body

        Jn = sum(impulse.normalImpulses)
        Jt = sum(impulse.tangentImpulses)

        normal = contact.worldManifold.normal
        tangent = b2Vec2(-normal.y, normal.x)

        FA = normal * Jn + tangent * Jt
        FB = -FA

        self.impulses.setdefault(bodyA, []).append(FA)
        self.impulses.setdefault(bodyB, []).append(FB)

    def BeginContact(self, contact):
        if self.function:
            self.function()
