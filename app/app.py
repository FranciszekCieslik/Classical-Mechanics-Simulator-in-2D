import pygame  # type: ignore
import thorpy as tp  # type: ignore
from obj.axes import Axes
from obj.camera import Camera
from obj.grid import Grid
from pygame import Surface  # type: ignore
from pygame.time import Clock  # type: ignore


class App:
    def __init__(self):
        self.screen: Surface = None
        self.grid: Grid = None
        self.axes: Axes = None
        self.camera: Camera = Camera()
        self.clock: Clock = Clock()
        self.width: int = 640
        self.height: int = 400
        self.size: tuple = (self.width, self.height)
        self._running: bool = True
        self.dragging: bool = False
        self.fullscreen: bool = False
        self.logo = None
        self.box = None

    def on_init(self):
        pygame.init()
        pygame.display.set_caption("Classical-Mechanics-Simulator-in-2D")
        flags = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE
        self.screen = pygame.display.set_mode(self.size, flags)
        self.grid = Grid(
            screen=self.screen, cell_size=100, color=(150, 150, 150), camera=self.camera
        )
        self.axes = Axes(screen=self.screen, grid=self.grid)
        self.logo = pygame.image.load("app//assets//logo.svg")
        pygame.display.set_icon(self.logo)  # ustaw ikonę
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

    def on_update(self):
        pass

    def on_render(self):
        self.screen.fill((220, 220, 220))
        self.grid.draw()
        self.axes.draw()
        pygame.display.flip()

    def on_cleanup(self):
        tp.quit()
        pygame.quit()

    def on_execute(self):
        if self.on_init() is False:
            self._running = False

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_update()
            self.on_render()
        self.on_cleanup()
