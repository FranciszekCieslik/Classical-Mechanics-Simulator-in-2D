import math

from Box2D import b2CircleShape, b2PolygonShape


def body_area(body):
    total_area = 0.0
    if body is None:
        return 0.0
    for fixture in body.fixtures:
        shape = fixture.shape
        if isinstance(shape, b2CircleShape):
            total_area += math.pi * shape.radius**2
        elif isinstance(shape, b2PolygonShape):
            verts = shape.vertices
            total_area += 0.5 * abs(
                sum(
                    x0 * y1 - x1 * y0
                    for (x0, y0), (x1, y1) in zip(verts, verts[1:] + verts[:1])
                )
            )
    return total_area
