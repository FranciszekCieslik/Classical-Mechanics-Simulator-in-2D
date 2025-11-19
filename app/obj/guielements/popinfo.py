import math
import thorpy as tp
from pygame import Vector2
from obj.realobject import RealObject
from Box2D import b2Vec2

def vector_to_scalar(vec:b2Vec2|Vector2):
    x,y = vec.x, vec.y
    scalar = x*x +y*y
    return math.sqrt(scalar)

class PopInfo:
    def __init__(self):
        self.pos = Vector2(0,0)
        self.offset = Vector2(0,0)
        self.time_left: int = 15
        self.text: str = "" 
        self.visible:bool = False

    def _text_gen(self, rlobj: RealObject):
        if rlobj.obj_type == 'static':
            self.text = 'Static object'
        else:
            body = rlobj.physics.body
            pos = body.position
            linearVelocity = body.linearVelocity
            self.text = ''