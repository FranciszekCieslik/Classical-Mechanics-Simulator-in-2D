import pygame
from Box2D import b2Vec2
from obj.camera import Camera
from obj.drawn.visualvector import VisualVector


class VectorComponents:
    def __init__(
        self,
        att_point: b2Vec2,
        value: b2Vec2,
        color: pygame.Color,
        camera: Camera,
        base_cell_size,
    ) -> None:
        self.components_color = color
        self.vector: VisualVector = VisualVector(
            att_point, value, color, camera, base_cell_size
        )
        self.vec_x: VisualVector = VisualVector(
            att_point, b2Vec2(value.x, 0), self.components_color, camera, base_cell_size
        )
        self.vec_y: VisualVector = VisualVector(
            att_point, b2Vec2(0, value.y), self.components_color, camera, base_cell_size
        )

    def draw(self) -> None:
        if not self.vector.visible:
            return
        if self.vector.value == b2Vec2(0, 0):
            return
        self.vector.draw()
        if self.show_comp:
            self.vec_x.draw()
            self.vec_y.draw()

    def set_value(self, val: b2Vec2) -> None:
        self.vector.set_value(val)
        self.vec_x.set_value(b2Vec2(val.x, 0))
        self.vec_y.set_value(b2Vec2(0, val.y))

    def update(self, att_p: b2Vec2, val: b2Vec2) -> None:
        self.set_value(val)
        self.vector.attachment_point = att_p
        self.vec_x.attachment_point = att_p
        self.vec_y.attachment_point = att_p
        self.show_comp = self.vec_x.visible and self.vec_y.visible

    def show_vector(self):
        self.vector.visible = True

    def hide_vector(self):
        self.vector.visible = False

    def show_components(self):
        self.vec_x.visible = True
        self.vec_y.visible = True

    def hide_components(self):
        self.vec_x.visible = False
        self.vec_y.visible = False

    def set_components_color(self, color: pygame.Color) -> None:
        self.vec_x.color = self.vec_y.color = color

    def show(self):
        self.show_components()
        self.show_vector()
