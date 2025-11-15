from Box2D import b2ContactListener, b2Vec2


class ImpulseCollector(b2ContactListener):
    def __init__(self):
        super().__init__()
        self.impulses = {}  # body -> dict with normal/tangent

    def PostSolve(self, contact, impulse):
        bodyA = contact.fixtureA.body
        bodyB = contact.fixtureB.body

        # Suma impulsów po wszystkich punktach kontaktu
        Jn = sum(impulse.normalImpulses)
        Jt = sum(impulse.tangentImpulses)

        normal = contact.worldManifold.normal
        tangent = b2Vec2(-normal.y, normal.x)

        FA = normal * Jn + tangent * Jt
        FB = -FA

        # Zapisujemy dla bodyA
        self.impulses.setdefault(bodyA, []).append(FA)
        # oraz dla bodyB
        self.impulses.setdefault(bodyB, []).append(FB)
