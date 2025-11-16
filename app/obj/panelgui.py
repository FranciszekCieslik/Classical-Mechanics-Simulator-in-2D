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
        objmanager: ObjectsManager,
        draw_assistance: DrawAssistance,
    ):
        self.screen: pygame.Surface = pygame.display.get_surface()

        self.metagroup: Optional[tp.Group] = None

        self.group_draw: Optional[tp.Group] = None
        self.group_simulation: Optional[tp.Group] = None
        self.group_ext: Optional[tp.Group] = None
        self.group_color: Optional[tp.Group] = None

        self.gravity_input: Optional[NumberInputOnCheckbox] = None

        self.helpers: list[tp.Helper] = []

        self.objects_manager = objmanager
        self.draw_assistance = draw_assistance
        self.button_play: Optional[tp.ImageButton] = None
        self.is_rubber_on: bool = False
        self.on_init()

    def on_init(self):

        ico_paths = [
            # "app/assets/icons/line.svg",
            "app/assets/icons/rectangle.svg",
            "app/assets/icons/circle.svg",
            "app/assets/icons/triangle.svg",
            "app/assets/icons/rubber.svg",
        ]
        draw_labels = [
            # "Line",
            "Rectangle",
            "Circle",
            "Triangle",
            "Rubber",
        ]

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
            "app/assets/icons/check_point.svg",
        ]
        sim_labels = ["Start/Pause", "Reset", "Point particle"]

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
                btn._at_click = self.objects_manager.reset_simulation
            elif "point" in icon_path:
                btn._at_click = lambda: self.draw_assistance.active_drawing(
                    "point_particle"
                )
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

        self.group_ext = tp.Group([text_group1], "v", gap=5, align="right")

        self.color_palette = ColorPalette()
        self.group_color = self.color_palette.get()
        self.metagroup = tp.Group(
            [self.group_draw, self.group_simulation, self.group_ext, self.group_color]
        )
        self.metagroup.sort_children("h", gap=30)
        self.metagroup.set_size(self.screen.get_size())
        self.mainbox = tp.Box([self.metagroup])
        self.mainbox.set_topleft(0, 0)
        self.mainbox.set_bck_color((0, 0, 0))

    def after_update(self):
        self.draw_assistance.set_color(self.color_palette.selected_color)
        self.color_palette.update_color_preview()

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
