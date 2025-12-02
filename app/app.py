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
        self.objectsmanager: ObjectsManager = ObjectsManager(
            surface=self.screen,
            camera=self.camera,
            cell_size=self.grid.base_cell_size,
            gravity=(0.0, 9.8),
        )

        # --- Draw Assistance ---
        self.draw_assistance = DrawAssistance(
            self.screen, self.camera, self.grid.base_cell_size
        )

        # --- Thorpy Init ---
        tp.init(self.screen, theme=tp.theme_text_dark)
        tp.set_default_font(font_name="console", font_size=12)

        # --- GUI PANEL ---
        self.panelgui: Panel_GUI = Panel_GUI(
            objectsmanager=self.objectsmanager, draw_assistance=self.draw_assistance
        )
        self.objectsmanager.stoper = self.panelgui.stoper
        self.objectsmanager.un_play = lambda: self.panelgui.button_play.set_value(False)
        # --- Side Bar ---
        self.objsidebar: SideBar = SideBar(self.objectsmanager)
        self.point_particle_sidebar: PointParticleSideBar = PointParticleSideBar(
            self.objectsmanager
        )
        # --- Pop Inf ---
        self.pop_info = PopInfo(self.camera, self.objectsmanager)

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
            # --- KEY EVENTS ---
        elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                pygame.display.iconify()
            elif event.key == pygame.K_UP:
                self.camera.move(dy=10)
            elif event.key == pygame.K_DOWN:
                self.camera.move(dy=-10)
            elif event.key == pygame.K_LEFT:
                self.camera.move(dx=10)
            elif event.key == pygame.K_RIGHT:
                self.camera.move(dx=-10)

            # --- MOUSE EVENTS ---
        elif (
            event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP
        ) and event.button == 1:
            self._at_left_mouse_button(event)
        elif (
            event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP
        ) and event.button == 2:
            obj = self.objectsmanager.selected_obj
            if obj:
                self.pop_info.update(obj)
        elif (
            event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP
        ) and event.button == 3:
            obj = self.objectsmanager.selected_obj
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
        elif event.type == pygame.MOUSEMOTION:
            pass
        elif event.type == pygame.MOUSEWHEEL:
            if not self.draw_assistance.is_drawing:
                factor = (
                    self.camera.zoom_speed
                    if event.y > 0
                    else 1.0 / self.camera.zoom_speed
                )
                self.camera.zoom_at(factor, pygame.mouse.get_pos())
        else:
            self.dragging = False
            self.prev_mouse_pos = None
            self.objectsmanager.end_dragging_obj()

    def on_update(self) -> None:
        pos = pygame.mouse.get_pos()
        current_mouse_pos = pygame.Vector2(pos)
        if not self.objectsmanager.selected_obj_is_being_dragged:
            self.objectsmanager.select_object_at_position(pos)

        if self.draw_assistance.is_drawing:
            self.draw_assistance.set_current_position(pos)
        elif self.prev_mouse_pos:
            delta = current_mouse_pos - self.prev_mouse_pos
            if self.dragging:
                self.camera.move(delta.x, delta.y)
                self.prev_mouse_pos = current_mouse_pos
            elif self.objectsmanager.selected_obj_is_being_dragged:
                diff = self.camera.screen_to_world(
                    self.prev_mouse_pos
                ) - self.camera.screen_to_world(current_mouse_pos)
                self.objectsmanager.move_selected_obj(diff * self.camera.zoom)
                self.prev_mouse_pos = current_mouse_pos

        self.objectsmanager.step_simulation()

    def draw_panels(self):
        self.objsidebar.update()
        if not self.objsidebar.visible:
            self.point_particle_sidebar.update()
        self.panels_launcher.update(func_after=self.panelgui.after_update)

    def on_render(self) -> None:
        self.screen.fill((220, 220, 220))
        self.grid.draw()
        self.axes.draw()
        self.draw_assistance.draw()
        self.objectsmanager.draw_objects()
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
            self.clock.tick(100)

        self.on_cleanup()

    def toggle_simulation(self, running: bool) -> None:
        self.objectsmanager.is_simulation_running = running

    def _at_left_mouse_button(self, event) -> None:
        if self.panelgui.is_rubber_on:
            if self.objectsmanager.selected_obj:
                for i, old_obj in enumerate(self.objectsmanager.objects):
                    if old_obj == self.objectsmanager.selected_obj:
                        self.objectsmanager.objects[i].destroy()
                        self.objectsmanager.objects.pop(i)
                self.objectsmanager.selected_obj = None
                self.panelgui.is_rubber_on = False
            self.objectsmanager.end_dragging_obj()
            self.dragging = False
        elif self.draw_assistance.is_drawing:
            if (
                self.draw_assistance.start_pos is None
                and event.type == pygame.MOUSEBUTTONDOWN
            ):
                self.draw_assistance.set_start_position(pygame.mouse.get_pos())
            elif (
                self.draw_assistance.state == 'triangle'
                and self.draw_assistance.third_triangel_point is None
            ):
                self.draw_assistance.set_third_triangle_point(pygame.mouse.get_pos())
            else:
                self.prev_mouse_pos = None
                result = self.draw_assistance.deactivate_drawing()
                if result is not None:
                    state, position, size, color = result
                    self.objectsmanager.add_object(
                        obj_type="static",
                        shape_type=state,
                        size=size,
                        position=position,
                        angle=0.00,
                        color=color,
                        features=None,
                    )
        else:
            if self.objectsmanager.selected_obj_is_being_dragged:
                self.objectsmanager.end_dragging_obj()
                self.prev_mouse_pos = None
            else:
                obj = self.objectsmanager.selected_obj
                self.prev_mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
                if obj:
                    self.objectsmanager.selected_obj_is_being_dragged = True
                elif not self.dragging:
                    self.objectsmanager.end_dragging_obj()
                    self.dragging = True
                else:
                    self.objectsmanager.end_dragging_obj()
                    self.dragging = False
                    self.prev_mouse_pos = None
