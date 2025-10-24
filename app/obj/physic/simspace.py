from Box2D import b2World


class SimSpace:
    def __init__(self, gravity: float = 0.00) -> None:
        worldDef: b2World = b2World(gravity=(0, -gravity), doSleep=True)
