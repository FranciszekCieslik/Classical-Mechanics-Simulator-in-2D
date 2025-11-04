import threading
import time
from typing import Callable, Optional

import pygame  # type: ignore
from obj.axes import Axes
from obj.camera import Camera
from obj.drawassistance import DrawAssistance
from obj.grid import Grid
from obj.objectsmanager import ObjectsManager
from obj.panelgui import Panel_GUI
from obj.physicobject import Features
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

        # --- OBJECTS MANAGER ---
        self.objmanager: ObjectsManager = ObjectsManager(
            surface=self.screen,
            camera=self.camera,
            cell_size=self.grid.base_cell_size,
            gravity=(0.0, -9.8),
        )

        # --- Draw Assistance ---
        self.draw_assistance = DrawAssistance(self.screen)

        # --- GUI PANEL ---
        self.panel_surface: Surface = pygame.Surface(
            (self.screen.get_width(), 80), flags=pygame.SRCALPHA
        )
        self.panel_rect: Rect = self.panel_surface.get_rect(topleft=(0, 0))
        self.panelgui: Panel_GUI = Panel_GUI(
            self.panel_surface, self.objmanager, self.draw_assistance
        )

        # --- TIMING ---
        self.clock: Clock = Clock()
        self._resize_lock: threading.Lock = threading.Lock()
        self._last_resize: float = 0.0
        self._resize_cooldown: float = 0.2
        self.DOUBLE_CLICK_TIME = 400  # maksymalny odstęp (ms) między kliknięciami
        self.last_click_time = 0.0

        # --- FLAGS ---
        self._running: bool = True
        self.dragging: bool = False
        self.minimized: bool = False

        # --- PREV MOUSE POS ---
        self.prev_mouse_pos: Optional[pygame.Vector2] = None

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
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.draw_assistance.is_drawing:
                    if self.draw_assistance.start_pos is None:
                        self.draw_assistance.set_start_position(event.pos)
                    elif (
                        self.draw_assistance.state == 'triangle'
                        and self.draw_assistance.third_triangel_point is None
                    ):
                        self.draw_assistance.set_third_triangle_point(event.pos)
                else:
                    now = time.time() * 1000.0
                    if now - self.last_click_time <= self.DOUBLE_CLICK_TIME:
                        obj = self.objmanager.select_object_at_position(event.pos)
                        if obj:
                            self.objmanager.selected_obj_is_being_dragged = True
                            self.prev_mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
                            print(
                                "Obj state:",
                                obj.physics.is_static,
                                obj.physics.shape_type,
                            )
                    self.last_click_time = now
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                result = self.draw_assistance.deactivate_drawing(
                    self.camera, self.grid.base_cell_size
                )
                if result is not None:
                    state, pos, size, color = result
                    # print("DEBUG:", state, pos, size, color)
                    self.objmanager.add_object(
                        obj_type="static",
                        shape_type=state,
                        size=size,
                        position=pos,
                        angle=0.00,
                        color=color,
                        features=None,
                    )
                #  --- dragging obj ---
                self.objmanager.end_dragging_obj()
                self.prev_mouse_pos = None
            elif event.type == pygame.MOUSEMOTION and self.draw_assistance.is_drawing:
                self.draw_assistance.set_current_position(event.pos)

                # --- POSITION UPDATE ---
            if self.objmanager.selected_obj_is_being_dragged:
                pos = pygame.Vector2(pygame.mouse.get_pos())
                if pos != self.prev_mouse_pos and self.objmanager.selected_obj:
                    d = self.prev_mouse_pos - pygame.Vector2(pos)
                    self.objmanager.selected_obj.move(d)
                    self.prev_mouse_pos = pos

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
        self.objmanager.step_simulation()

    def draw_panel(self):
        self.panelgui.render()
        self.screen.blit(self.panel_surface, self.panel_rect)

    def on_render(self) -> None:
        if getattr(self, "minimized", False):
            return

        self.screen.fill((220, 220, 220))
        self.grid.draw()
        self.axes.draw()
        self.objmanager.draw_objects()
        self.draw_assistance.draw()
        self.draw_panel()

    def on_cleanup(self) -> None:
        pygame.quit()

    def on_execute(self) -> None:

        self.objmanager.add_object(
            obj_type="static",
            shape_type="rectangle",
            size=(8, 1),
            position=(0, 0),
            angle=00.0,
            color=pygame.Vector3(150, 150, 255),
        )

        dyn_features = Features(density=1.0, friction=0.4, restitution=0.3)
        self.objmanager.add_object(
            obj_type="dynamic",
            shape_type="rectangle",
            size=(1, 1),
            position=(-5, 3),
            angle=45.0,
            color=pygame.Vector3(255, 80, 80),
            features=dyn_features,
        )
        self.objmanager.add_object(
            obj_type="dynamic",
            shape_type="rectangle",
            size=(1, 1),
            position=(0, 3),
            angle=45.0,
            color=pygame.Vector3(255, 80, 80),
            features=dyn_features,
        )

        self.objmanager.add_object(
            obj_type="dynamic",
            shape_type="circle",
            size=0.8,
            position=(0, 20),
            angle=45.0,
            color=pygame.Vector3(255, 200, 0),
            features=dyn_features,
        )

        self.objmanager.add_object(
            obj_type="dynamic",
            shape_type="triangle",
            size=[(-2, 0), (2, 0), (0, 3)],
            position=(0, 14),
            angle=00.0,
            color=pygame.Vector3(80, 255, 80),
            features=dyn_features,
        )

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_update()
            self.on_render()
            pygame.display.flip()
            self.clock.tick(60)

        self.on_cleanup()

    def toggle_simulation(self, running: bool) -> None:
        self.objmanager.is_simulation_running = running
