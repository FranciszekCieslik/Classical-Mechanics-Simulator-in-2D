from typing import Optional

import pygame
import thorpy as tp
from obj.drawassistance import DrawAssistance
from obj.guielements.colorpalette import ColorPalette
from obj.guielements.numinputoncheckbox import NumberInputOnCheckbox
from obj.guielements.toggleimagebutton import ToggleImageButton
from obj.objectsmanager import ObjectsManager


class Panel_GUI:
    def __init__(
        self,
        screen: pygame.Surface,
        objmanager: ObjectsManager,
        draw_assistance: DrawAssistance,
    ):
        self.screen = screen
        self.metagroup: Optional[tp.Group] = None
        self.launcher: Optional[tp.Loop] = None

        self.group_draw: Optional[tp.Group] = None
        self.group_simulation: Optional[tp.Group] = None
        self.group_ext: Optional[tp.Group] = None
        self.group_color: Optional[tp.Group] = None

        self.gravity_input: Optional[NumberInputOnCheckbox] = None
        self.checkbox_obj_as_points: Optional[tp.Checkbox] = None

        self.helpers: list[tp.Helper] = []

        self.objects_manager = objmanager
        self.draw_assistance = draw_assistance
        self.button_play: Optional[tp.ImageButton] = None
        self.is_rubber_on: bool = False
        self.on_init()

    def on_init(self):
        # --- inicjalizacja Thorpy ---
        tp.init(self.screen, theme=tp.theme_text_dark)
        tp.set_default_font(font_name="console", font_size=12)

        # === Przyciski rysowania ===
        ico_paths = [
            "app/assets/icons/line.svg",
            "app/assets/icons/rectangle.svg",
            "app/assets/icons/circle.svg",
            "app/assets/icons/triangle.svg",
            "app/assets/icons/rubber.svg",
        ]
        draw_labels = ["Line", "Rectangle", "Circle", "Triangle", "Rubber"]

        draw_buttons = []
        for icon_path, label in zip(ico_paths, draw_labels):
            img = pygame.image.load(icon_path)
            img = pygame.transform.smoothscale(img, (30, 30))
            variant = tp.graphics.change_color_on_img(
                img, img.get_at((0, 0)), (100, 100, 100)
            )
            btn = tp.ImageButton("", img.copy(), img_hover=variant)
            if "rectangle" in icon_path:
                btn._at_click = lambda: self.draw_assistance.active_drawing("rectangle")
            elif "circle" in icon_path:
                btn._at_click = lambda: self.draw_assistance.active_drawing("circle")
            elif "triangle" in icon_path:
                btn._at_click = lambda: self.draw_assistance.active_drawing("triangle")
            elif "line" in icon_path:
                btn._at_click = lambda: self.draw_assistance.active_drawing("line")
            elif "rubber" in icon_path:

                def on_rubber_click():
                    self.is_rubber_on = not self.is_rubber_on

                btn._at_click = on_rubber_click

            helper = tp.Helper(label, btn, countdown=30, offset=(0, 40))
            helper.set_font_size(12)
            self.helpers.append(helper)
            draw_buttons.append(btn)
        self.group_draw = tp.Group(draw_buttons, "h")

        # === Przyciski symulacji (Play/Stop + inne) ===
        sim_icons = [
            "app/assets/icons/play.svg",
            "app/assets/icons/reset.svg",
            "app/assets/icons/vector-two-fill.svg",
        ]
        sim_labels = ["Start/Pause", "Reset", "Simulation Space"]

        sim_buttons = []

        for icon_path, label in zip(sim_icons, sim_labels):
            img = pygame.image.load(icon_path)
            img = pygame.transform.smoothscale(img, (30, 30))
            variant = tp.graphics.change_color_on_img(
                img, img.get_at((0, 0)), (100, 100, 100)
            )

            # --- Play/Stop ---
            if "play.svg" in icon_path:
                # --- Wczytanie ikon ---
                img_play = pygame.image.load("app/assets/icons/play.svg")
                img_play = pygame.transform.smoothscale(img_play, (30, 30))
                img_play_hover = tp.graphics.change_color_on_img(
                    img_play, img_play.get_at((0, 0)), (100, 100, 100)
                )

                img_stop = pygame.image.load("app/assets/icons/stop.svg")
                img_stop = pygame.transform.smoothscale(img_stop, (30, 30))
                img_stop_hover = tp.graphics.change_color_on_img(
                    img_stop, img_stop.get_at((0, 0)), (100, 100, 100)
                )

                self.button_play = ToggleImageButton(
                    text="",
                    img=img_play,
                    img_hover=img_play_hover,
                    img_pressed=img_stop,
                    img_pressed_hover=img_stop_hover,
                    no_copy=False,
                    value=False,
                    on_toggle=self.objects_manager.run_simulation,
                )
                btn = self.button_play
            else:
                btn = tp.ImageButton("", img.copy(), img_hover=variant)
            if label == "Reset":
                btn._at_click = self.objects_manager.reset_simulation()
            helper = tp.Helper(label, btn, countdown=30, offset=(0, 40))
            helper.set_font_size(12)
            self.helpers.append(helper)
            sim_buttons.append(btn)

        self.group_simulation = tp.Group(sim_buttons, "h")

        self.gravity_input = NumberInputOnCheckbox(
            checkbox_text="GRAVITY",
            input_text="9.8",
            fun=self.objects_manager.set_gravity_force,
            input_placeholder="9.8",
        )
        text_group1 = self.gravity_input.get()

        self.checkbox_obj_as_points = tp.Checkbox()
        text_group2 = tp.Group(
            [
                self.checkbox_obj_as_points,
                tp.Text("TREAT OBJECTS AS POINTS", font_size=12),
            ],
            "h",
            gap=10,
        )

        self.group_ext = tp.Group([text_group1, text_group2], "v", gap=5, align="right")

        # === Color Picker (wbudowany w panel, nie popup) ===
        self.color_palette = ColorPalette()
        self.group_color = self.color_palette.get()
        # === Łączenie wszystkich grup ===
        self.metagroup = tp.Group(
            [self.group_draw, self.group_simulation, self.group_ext, self.group_color]
        )
        self.metagroup.sort_children("h", gap=30)
        self.metagroup.set_size(self.screen.get_size())
        self.mainbox = tp.Box([self.metagroup])
        self.mainbox.set_topleft(0, 0)
        self.launcher = self.mainbox.get_updater()

    def after_update(self):
        self.draw_assistance.set_color(self.color_palette.selected_color)
        self.color_palette.update_color_preview()

    def render(self):
        if self.launcher:
            self.launcher.update(func_after=self.after_update)

    def resize_panel(self, panel_surface: pygame.Surface):
        self.screen = panel_surface
        tp.set_screen(self.screen)
        if self.metagroup is not None:
            self.set_screen_recursive(self.metagroup, self.screen)
            self.metagroup.set_size(self.screen.get_size())
            self.metagroup.set_topleft(0, 10)
            self.launcher = self.metagroup.get_updater()
            self.launcher.update()

    def set_screen_recursive(self, element, new_surface):
        if element is None:
            return
        if hasattr(element, "surface"):
            element.surface = new_surface
        if hasattr(element, "screen"):
            element.screen = new_surface
        if hasattr(element, "children"):
            for child in element.children:
                self.set_screen_recursive(child, new_surface)
