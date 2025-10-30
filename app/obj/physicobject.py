from typing import List, Optional, Tuple, Union

from Box2D import (
    b2CircleShape,
    b2PolygonShape,
    b2Vec2,
    b2World,
)

# Typy geometryczne
RectangleSize = Tuple[float, float]
TriangleVertices = List[Tuple[float, float]]
CircleRadius = float
ShapeSize = Union[RectangleSize, TriangleVertices, CircleRadius]


class Features:
    """Defines physical properties for a Box2D body."""

    def __init__(
        self,
        linearVelocity: Tuple[float, float] = (0.0, 0.0),
        angularVelocity: float = 0.0,
        linearDamping: float = 0.0,
        angularDamping: float = 0.0,
        density: float = 1.0,
        friction: float = 0.3,
        restitution: float = 0.0,
        fixedRotation: bool = False,
        active: bool = True,
    ) -> None:
        self.linearVelocity = linearVelocity
        self.angularVelocity = angularVelocity
        self.linearDamping = linearDamping
        self.angularDamping = angularDamping
        self.density = density
        self.friction = friction
        self.restitution = restitution
        self.fixedRotation = fixedRotation
        self.active = active


class PhysicObject:
    """Creates a static or dynamic physical object in a Box2D world."""

    def __init__(
        self,
        type: str,
        shape: str,
        size: ShapeSize,
        position: Tuple[float, float],
        angle: float,
        world: b2World,
        features: Optional[Features] = None,
    ) -> None:
        self.is_static = type.lower() == "static"
        self.shape_type = shape.lower()
        self.world = world
        self.position = position
        self.angle = angle

        if features is None:
            features = Features()

        # Create body
        if self.is_static:
            self.body = world.CreateStaticBody(position=position, angle=angle)
        else:
            self.body = world.CreateDynamicBody(
                position=position,
                angle=angle,
                linearVelocity=b2Vec2(*features.linearVelocity),
                angularVelocity=features.angularVelocity,
                linearDamping=features.linearDamping,
                angularDamping=features.angularDamping,
                fixedRotation=features.fixedRotation,
                active=features.active,
            )

        # Create shape depending on type
        shape_obj = self._create_shape(shape=self.shape_type, size=size)

        # Create fixture
        self.fixture = self.body.CreateFixture(
            shape=shape_obj,
            density=features.density if not self.is_static else 0.0,
            friction=features.friction,
            restitution=features.restitution,
        )

    # -------------------------------------------
    def _create_shape(self, shape: str, size: ShapeSize):
        """Internal helper to create a Box2D shape object."""
        if shape == "rectangle":
            if not (isinstance(size, (tuple, list)) and len(size) == 2):
                raise TypeError("Rectangle shape requires size=(width, height).")
            return b2PolygonShape(box=size)

        elif shape == "circle":
            if not isinstance(size, (int, float)):
                raise TypeError("Circle shape requires size=radius (float).")
            return b2CircleShape(radius=size)

        elif shape == "triangle":
            if not (isinstance(size, list) and len(size) == 3):
                raise TypeError(
                    "Triangle shape requires 3 vertex points [(x1,y1),(x2,y2),(x3,y3)]."
                )
            return b2PolygonShape(vertices=size)

        else:
            raise ValueError(f"Unsupported shape type: {shape}")

    # -------------------------------------------
    def set_body_mass(self, mass: float) -> None:
        """Adjusts body mass by scaling its density proportionally."""
        if not hasattr(self, "body") or self.body is None:
            raise ValueError("Body has not been created.")

        current_mass = self.body.mass
        if current_mass <= 0:
            raise ValueError("Cannot set mass — body has no valid density or fixtures.")

        scale = mass / current_mass

        for fixture in self.body.fixtures:
            fixture.density *= scale

        self.body.ResetMassData()

    # -------------------------------------------
    def get_mass(self) -> float:
        """Returns the current mass of the body."""
        return self.body.mass if self.body else 0.0

    # -------------------------------------------
    def apply_force(
        self, force: Tuple[float, float], point: Optional[Tuple[float, float]] = None
    ) -> None:
        """Applies a force to the body at the given world point."""
        if self.is_static:
            raise ValueError("Cannot apply force to a static body.")
        if point is None:
            point = self.body.worldCenter
        self.body.ApplyForce(force=b2Vec2(*force), point=b2Vec2(*point), wake=True)
