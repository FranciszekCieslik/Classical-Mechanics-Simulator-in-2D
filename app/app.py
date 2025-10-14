import pygame  # type: ignore
from obj.axes import Axes
from obj.camera import Camera
from obj.grid import Grid


class App:
    def __init__(self):
        self._running = True
        self.screen = None
        self.grid = None
        self.axes = None
        self.camera = Camera()
        self.fullscreen = False
        self.clock = pygame.time.Clock()
        self.width, self.height = 640, 400
        self.size = (self.width, self.height)
        self.dragging = False

    def on_init(self):
        pygame.init()
        pygame.display.set_caption("Classical-Mechanics-Simulator-in-2D")
        flags = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE
        self.screen = pygame.display.set_mode(self.size, flags)
        self.grid = Grid(
            screen=self.screen, cell_size=100, color=(150, 150, 150), camera=self.camera
        )
        self.axes = Axes(screen=self.screen, grid=self.grid)
        self._running = True

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                self.fullscreen = not self.fullscreen
                if self.fullscreen:
                    self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    flags = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE
                    self.screen = pygame.display.set_mode(self.size, flags)
                self.grid.screen = self.screen
                self.axes.screen = self.screen
        elif event.type == pygame.VIDEORESIZE:
            width, height = event.size
            self.size = (width, height)
            flags = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE
            self.screen = pygame.display.set_mode(self.size, flags)
            self.grid.screen = self.screen
            self.axes.screen = self.screen
            self.grid.resize()

        if event.type == pygame.MOUSEWHEEL:
            factor = (
                self.camera.zoom_speed if event.y > 0 else 1.0 / self.camera.zoom_speed
            )
            self.camera.zoom_at(factor, pygame.mouse.get_pos())

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
            pygame.mouse.get_rel()
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 2:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.camera.move(*pygame.mouse.get_rel())

    def on_loop(self):
        # dt = self.clock.get_time() / 1000.0
        pass

    def on_render(self):
        self.screen.fill((220, 220, 220))
        self.grid.draw()
        self.axes.draw()
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() is False:
            self._running = False

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
            self.clock.tick(90)
        self.on_cleanup()
