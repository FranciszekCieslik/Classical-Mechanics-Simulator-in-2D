from typing import Optional

import pygame
import thorpy as tp
from obj.drawassistance import DrawAssistance
from obj.objectsmanager import ObjectsManager
from obj.toggleimagebutton import ToggleImageButton


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

        self.checkbox_gravity: Optional[tp.Checkbox] = None
        self.checkbox_obj_as_points: Optional[tp.Checkbox] = None

        self.helpers: list[tp.Helper] = []

        self.objects_manager = objmanager
        self.draw_assistance = draw_assistance
        self.button_play: Optional[tp.ImageButton] = None
        self.on_init()

    def on_init(self):
        # --- inicjalizacja Thorpy ---
        main_screen = pygame.display.get_surface()
        tp.init(main_screen, theme=tp.theme_text_dark)
        tp.set_default_font(font_name="console", font_size=12)
        tp.set_screen(self.screen)

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

                def on_rectangle_click():
                    self.draw_assistance.active_drawing("rectangle")

                btn._at_click = on_rectangle_click
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

                def on_simulation_toggle(is_running: bool):
                    if is_running:
                        self.objects_manager.is_simulation_running = True
                    else:
                        self.objects_manager.is_simulation_running = False

                # --- Tworzenie przycisku ---
                self.button_play = ToggleImageButton(
                    text="",
                    img=img_play,
                    img_hover=img_play_hover,
                    img_pressed=img_stop,
                    img_pressed_hover=img_stop_hover,
                    no_copy=False,
                    value=False,
                    on_toggle=on_simulation_toggle,
                )

                btn = self.button_play

            else:
                btn = tp.ImageButton("", img.copy(), img_hover=variant)
            helper = tp.Helper(label, btn, countdown=30, offset=(0, 40))
            helper.set_font_size(12)
            self.helpers.append(helper)
            if label == "Reset":

                def on_reset_click():
                    if self.objects_manager:
                        self.objects_manager.reset_simulation()

                btn._at_click = on_reset_click
            sim_buttons.append(btn)

        self.group_simulation = tp.Group(sim_buttons, "h")

        # === Checkboxy ===
        self.checkbox_gravity = tp.Checkbox()
        text_group1 = tp.Group(
            [tp.Text("GRAVITY", font_size=12), self.checkbox_gravity], "h", gap=10
        )

        self.checkbox_obj_as_points = tp.Checkbox()
        text_group2 = tp.Group(
            [
                tp.Text("TREAT OBJECTS AS POINTS", font_size=12),
                self.checkbox_obj_as_points,
            ],
            "h",
            gap=10,
        )

        self.group_ext = tp.Group([text_group1, text_group2], "v", gap=5, align="right")

        # === Color Picker (wbudowany w panel, nie popup) ===
        label_color = tp.Text("COLOR PICKER", font_size=12)
        picker_predef = tp.ColorPickerPredefined(
            [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 255, 255)],
            mode="h",
            col_size=(20, 20),
        )
        self.group_color = tp.Group([label_color, picker_predef], "v", gap=1)

        # === Łączenie wszystkich grup ===
        self.metagroup = tp.Group(
            [self.group_draw, self.group_simulation, self.group_ext, self.group_color]
        )
        self.metagroup.sort_children("h", gap=30)
        self.metagroup.set_size(self.screen.get_size())
        self.metagroup.set_topleft(0, 10)
        self.launcher = self.metagroup.get_updater()

    def render(self):
        self.screen.fill((30, 30, 30))
        if self.launcher:
            self.launcher.update()

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
