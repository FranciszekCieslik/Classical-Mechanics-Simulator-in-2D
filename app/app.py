import threading
import time

import pygame  # type: ignore
import thorpy as tp  # type: ignore
from obj.axes import Axes
from obj.camera import Camera
from obj.drawn.rectangle import Rectangle
from obj.grid import Grid
from obj.panelgui import Panel_GUI
from pygame import Rect, Surface  # type: ignore
from pygame.time import Clock  # type: ignore


class App:
    def __init__(self) -> None:
        # --- WINDOW INIT ---
        pygame.init()
        info = pygame.display.Info()
        self.size: tuple[int, int] = (info.current_w, info.current_h)
        self.fullscreen: bool = True
        self.screen: Surface = pygame.display.set_mode(self.size, pygame.NOFRAME)
        pygame.display.set_caption("Classical-Mechanics-Simulator-in-2D")

        # logo
        self.logo: Surface = pygame.image.load("app/assets/logo.svg")
        pygame.display.set_icon(self.logo)

        # --- GUI PANEL ---
        self.panel_surface: Surface = pygame.Surface(
            (self.screen.get_width(), 80), flags=pygame.SRCALPHA
        )
        self.panel_rect: Rect = self.panel_surface.get_rect(topleft=(0, 0))
        self.panelgui: Panel_GUI = Panel_GUI(self.panel_surface)

        # --- CAMERA ---
        self.camera: Camera = Camera()

        # --- GRID and AXES ---
        self.grid: Grid = Grid(
            screen=self.screen,
            cell_size=100,
            color=(150, 150, 150),
            camera=self.camera,
        )
        self.axes: Axes = Axes(screen=self.screen, grid=self.grid)

        # --- TIMING ---
        self.clock: Clock = Clock()
        self._resize_lock: threading.Lock = threading.Lock()
        self._last_resize: float = 0.0
        self._resize_cooldown: float = 0.2

        # --- FLAGS ---
        self._running: bool = True
        self.dragging: bool = False
        self.minimized: bool = False

    def resize(self, event) -> None:
        now = time.time()
        if now - getattr(self, "_last_resize", 0) < self._resize_cooldown:
            return
        self._last_resize = now

        # ustal rozmiar okna niezależnie od typu eventu
        if hasattr(event, "size"):
            width, height = event.size
        elif hasattr(event, "data1") and hasattr(event, "data2"):
            width, height = event.data1, event.data2
        else:
            return

        with self._resize_lock:
            flags = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE
            self.size = (width, height)
            self.screen = pygame.display.set_mode(self.size, flags)

            # --- aktualizacja panelu ---
            panel_height = 80
            self.panel_surface = pygame.Surface(
                (self.screen.get_width(), panel_height), flags=pygame.RESIZABLE
            )
            self.panel_rect = self.panel_surface.get_rect(topleft=(0, 0))
            self.panelgui.screen = self.panel_surface
            self.panelgui.resize_panel(self.panel_surface)

    def on_event(self, event) -> None:
        # --- WINDOW EVENTS ---
        if event.type == pygame.QUIT:
            self._running = False
            return

        # if window is resaizeable
        # if event.type in (pygame.VIDEORESIZE, pygame.WINDOWRESIZED):
        #     self.resize(event)
        #     return

        # if event.type in (pygame.WINDOWRESTORED, pygame.WINDOWMAXIMIZED):
        #     if self.panelgui:
        #         self.panelgui.render()
        #     self.minimized = False
        #     return

        # if event.type == pygame.WINDOWMINIMIZED:
        #     self.minimized = True
        #     return

        # --- KEY EVENTS ---
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.display.iconify()
            return

        # --- MOUSE EVENTS ---
        # --- OUTSIDE THE PANEL ---
        if not self.panel_rect.collidepoint(pygame.mouse.get_pos()):
            if event.type == pygame.MOUSEWHEEL:
                factor = (
                    self.camera.zoom_speed
                    if event.y > 0
                    else 1.0 / self.camera.zoom_speed
                )
                self.camera.zoom_at(factor, pygame.mouse.get_pos())

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                pygame.mouse.get_rel()
                self.dragging = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 2:
                self.dragging = False
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                self.camera.move(*pygame.mouse.get_rel())

    def on_update(self) -> None:
        pass

    def draw_panel(self):
        self.panelgui.render()
        self.screen.blit(self.panel_surface, self.panel_rect)

    def on_render(self) -> None:
        if getattr(self, "minimized", False):
            return

        # rec = Rectangle(self.screen, self.camera, (-10,10), (255,0,0), (5,8), cell_size = 100)

        self.screen.fill((220, 220, 220))
        self.grid.draw()
        self.axes.draw()

        # rec.draw()

        self.draw_panel()
        pygame.display.flip()
        self.clock.tick(60)

    def on_cleanup(self) -> None:
        pygame.quit()

    def on_execute(self) -> None:

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_update()
            self.on_render()

        self.on_cleanup()
