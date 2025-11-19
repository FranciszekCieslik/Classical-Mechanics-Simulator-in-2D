import thorpy as tp
from obj.objectsmanager import ObjectsManager

class Timer:
    def __init__(self, objectsmanager: ObjectsManager):
        self.objectsmanager = objectsmanager
        fs = 14

        self.min = tp.Text("00", font_size=fs)
        self.seconds = tp.Text("00", font_size=fs)
        self.ms = tp.Text("000", font_size=fs)  # FIXED

        self.timer = tp.Group([
        tp.Text("Simulation Time", font_size=14),
        tp.Line("h",150),
        tp.Group(
            [self.min, tp.Text(':'), self.seconds, tp.Text(':'), self.ms],
            "h", gap=1
        )], "v", gap = 1
        )

    def get(self):
        return self.timer

    def update(self):
        t = self.objectsmanager.time

        total_ms = int(t * 1000)
        ms  = total_ms % 1000
        sec = (total_ms // 1000) % 60
        minu = total_ms // 60000

        self.ms.set_text(f"{ms:03}")
        self.seconds.set_text(f"{sec:02}")
        self.min.set_text(f"{minu:02}")
