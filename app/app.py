from typing import Optional

import pygame  # type: ignore
import thorpy as tp
from obj.axes import Axes
from obj.camera import Camera
from obj.drawassistance import DrawAssistance
from obj.grid import Grid
from obj.guielements.popinfo import PopInfo
from obj.guielements.sidebar.particle_sidebar import PointParticleSideBar
from obj.guielements.sidebar.sidebar import SideBar
from obj.objectsmanager import ObjectsManager
from obj.panelgui import Panel_GUI
from obj.physicobject import Features
from pygame import Surface  # type: ignore
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
            gravity=(0.0, 9.8),
        )

        # --- Draw Assistance ---
        self.draw_assistance = DrawAssistance(self.screen)

        # --- Thorpy Init ---
        tp.init(self.screen, theme=tp.theme_text_dark)
        tp.set_default_font(font_name="console", font_size=12)

        # --- GUI PANEL ---
        self.panelgui: Panel_GUI = Panel_GUI(
            objmanager=self.objmanager, draw_assistance=self.draw_assistance
        )
        self.objmanager.stoper = self.panelgui.stoper
        self.objmanager.un_play = lambda: self.panelgui.button_play.set_value(False)
        # --- Side Bar ---
        self.objsidebar: SideBar = SideBar(self.objmanager)
        self.point_particle_sidebar: PointParticleSideBar = PointParticleSideBar(
            self.objmanager
        )
        # --- Pop Inf ---
        self.pop_info = PopInfo(self.camera, self.objmanager)

        # --- Thorpy Launcher ---
        self.panels = tp.Group(
            [
                self.panelgui.mainbox,
                self.objsidebar.container,
                self.point_particle_sidebar.container,
                self.pop_info.get(),
            ],
            mode=None,
        )
        self.panels_launcher = self.panels.get_updater()
        # --- TIMING ---
        self.clock: Clock = Clock()

        # --- FLAGS ---
        self._running: bool = True
        self.dragging: bool = False

        # --- PREV MOUSE POS ---
        self.prev_mouse_pos: Optional[pygame.Vector2] = None

    def on_event(self, event) -> None:
        # --- WINDOW EVENTS ---
        if event.type == pygame.QUIT:
            self._running = False
            return

        # --- KEY EVENTS ---
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.display.iconify()
            return

        # --- MOUSE EVENTS ---
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.panelgui.is_rubber_on:
                if self.objmanager.selected_obj:
                    self.objmanager.objects.remove(self.objmanager.selected_obj)
                    self.panelgui.is_rubber_on = False
            elif self.draw_assistance.is_drawing:
                if self.draw_assistance.start_pos is None:
                    self.draw_assistance.set_start_position(pygame.mouse.get_pos())
                elif (
                    self.draw_assistance.state == 'triangle'
                    and self.draw_assistance.third_triangel_point is None
                ):
                    self.draw_assistance.set_third_triangle_point(
                        pygame.mouse.get_pos()
                    )
            elif self.panelgui.is_rubber_on:
                if self.objmanager.selected_obj:
                    self.objmanager.selected_obj.destroy()
                    self.objmanager.objects.remove(self.objmanager.selected_obj)
                    self.panelgui.is_rubber_on = False
            else:
                obj = self.objmanager.selected_obj
                if obj:
                    self.objmanager.selected_obj_is_being_dragged = True
                    self.prev_mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
                else:
                    self.objmanager.end_dragging_obj()
                    self.objmanager.selected_obj = None
                    if not self.draw_assistance.is_drawing:
                        self.dragging = True
                        self.prev_mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            self.objmanager.end_dragging_obj()
            self.prev_mouse_pos = None
            result = self.draw_assistance.deactivate_drawing(
                self.camera, self.grid.base_cell_size
            )
            if result is not None:
                state, pos, size, color = result
                self.objmanager.add_object(
                    obj_type="static",
                    shape_type=state,
                    size=size,
                    position=pos,
                    angle=0.00,
                    color=color,
                    features=None,
                )
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
            obj = self.objmanager.selected_obj
            if obj:
                self.pop_info.update(obj)
                self.objmanager.selected_obj_is_being_dragged = False
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 2:
            self.dragging = False
            self.prev_mouse_pos = None
            self.objmanager.end_dragging_obj()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            obj = self.objmanager.selected_obj
            if obj:
                if obj.shape_type != "point_particle":
                    self.objsidebar.get_data_from_real_obj(obj)
                    if (
                        not self.objsidebar.visible
                        and not self.point_particle_sidebar.visible
                    ):
                        self.objsidebar.show()
                elif obj.shape_type == "point_particle":
                    self.point_particle_sidebar.get_data_from_real_obj(obj)
                    if (
                        not self.objsidebar.visible
                        and not self.point_particle_sidebar.visible
                    ):
                        self.point_particle_sidebar.show()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            self.objmanager.end_dragging_obj()
            pass
        elif event.type == pygame.MOUSEMOTION:
            if self.draw_assistance.is_drawing:
                self.draw_assistance.set_current_position(pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEWHEEL:
            if not self.draw_assistance.is_drawing:
                factor = (
                    self.camera.zoom_speed
                    if event.y > 0
                    else 1.0 / self.camera.zoom_speed
                )
                self.camera.zoom_at(factor, pygame.mouse.get_pos())

    def on_update(self) -> None:
        pos = pygame.mouse.get_pos()
        current_mouse_pos = pygame.Vector2(pos)
        if (
            not self.objmanager.selected_obj_is_being_dragged
            and not self.draw_assistance.is_drawing
        ):
            self.objmanager.select_object_at_position(pos)
        if self.objmanager.selected_obj_is_being_dragged and self.prev_mouse_pos:
            if current_mouse_pos != self.prev_mouse_pos:
                delta = current_mouse_pos - self.prev_mouse_pos
                diff = self.camera.screen_to_world(
                    self.prev_mouse_pos
                ) - self.camera.screen_to_world(current_mouse_pos)
                self.objmanager.move_selected_obj(diff * self.camera.zoom)
                if not self.dragging:
                    self.prev_mouse_pos = current_mouse_pos
        if self.dragging and self.prev_mouse_pos:
            if current_mouse_pos != self.prev_mouse_pos:
                delta = current_mouse_pos - self.prev_mouse_pos
                self.camera.move(delta.x, delta.y)
                self.prev_mouse_pos = current_mouse_pos

        self.objmanager.step_simulation()

    def draw_panels(self):
        self.objsidebar.update()
        if not self.objsidebar.visible:
            self.point_particle_sidebar.update()
        self.panels_launcher.update(func_after=self.panelgui.after_update)

    def on_render(self) -> None:
        self.screen.fill((220, 220, 220))
        self.grid.draw()
        self.axes.draw()
        self.objmanager.draw_objects()
        self.draw_assistance.draw()
        self.draw_panels()

    def on_cleanup(self) -> None:
        pygame.quit()

    def on_execute(self) -> None:
        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_update()
            self.pop_info.tick()
            self.on_render()
            pygame.display.flip()
            self.clock.tick(200)

        self.on_cleanup()

    def toggle_simulation(self, running: bool) -> None:
        self.objmanager.is_simulation_running = running
