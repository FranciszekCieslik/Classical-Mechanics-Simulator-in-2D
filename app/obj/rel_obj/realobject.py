class RealObject:
    def __init__(self, type="rectangle", static=True, start_position=(0, 0)) -> None:
        self.type: str = type
        self.static: bool = static
        self.start_position: tuple = start_position
