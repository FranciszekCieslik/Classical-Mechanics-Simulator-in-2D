from typing import List, Optional, Tuple, Union

from Box2D import b2CircleShape, b2PolygonShape, b2Shape, b2Vec2, b2World

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
        obj_type: str,
        shape_type: str,
        size: ShapeSize,
        position: Tuple[float, float],
        angle: float,
        world: b2World,
        features: Optional[Features] = None,
    ):
        self.is_static = obj_type.lower() == "static"
        self.shape_type = shape_type.lower()
        self.world = world
        self.position = (position[0], position[1])
        self.angle = angle

        if features is None:
            features = Features()

        offset_y = 0.0
        local_vertices = None
        body_pos = (self.position[0], self.position[1])
        if self.shape_type == "triangle":
            if not isinstance(size, list):
                raise TypeError(
                    f"Expected list for triangle size, got {type(size).__name__}"
                )
            verts = [b2Vec2(v[0], v[1]) for v in size]
            centroid_x = sum(v.x for v in verts) / 3.0
            centroid_y = sum(v.y for v in verts) / 3.0

            if self.is_static:
                local_vertices = [
                    b2Vec2(v.x - centroid_x, v.y - centroid_y) for v in verts
                ]
                body_pos = (
                    self.position[0] + centroid_x,
                    self.position[1] + centroid_y,
                )
            else:
                local_vertices = verts
                body_pos = self.position
        elif self.shape_type == "rectangle":
            if not isinstance(size, tuple):
                raise TypeError(
                    f"Expected tuple for rectangle size, got {type(size).__name__}"
                )
            width, height = size
        elif self.shape_type == "circle":
            if not isinstance(size, float):
                raise TypeError(
                    f"Expected float for circle radius, got {type(size).__name__}"
                )
            radius = size

        if self.is_static:
            self.body = world.CreateStaticBody(position=body_pos, angle=angle)
        else:
            self.body = world.CreateDynamicBody(
                position=body_pos,
                angle=angle,
                linearVelocity=b2Vec2(*features.linearVelocity),
                angularVelocity=features.angularVelocity,
                linearDamping=features.linearDamping,
                angularDamping=features.angularDamping,
                fixedRotation=features.fixedRotation,
                active=features.active,
            )

        shape_obj = self._create_shape(self.shape_type, size, local_vertices)
        if self.shape_type != "circle":
            shape_obj.radius = 0.0022

        self.fixture = self.body.CreateFixture(
            shape=shape_obj,
            density=features.density if not self.is_static else 0.0,
            friction=features.friction,
            restitution=features.restitution,
        )

    def _create_shape(self, shape_type, size, local_vertices):
        if shape_type == "triangle":
            return b2PolygonShape(vertices=local_vertices)
        elif shape_type == "rectangle":
            width, height = size
            return b2PolygonShape(box=(width / 2, height / 2))
        elif shape_type == "circle":
            return b2CircleShape(radius=size)
        else:
            raise ValueError(f"Unknown shape type: {shape_type}")

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
