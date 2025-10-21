from typing import Optional

import pygame
import thorpy as tp


class Panel_GUI:
    def __init__(self, screen: pygame.Surface = None):
        self.screen: Optional[pygame.Surface] = screen
        self.metagroup: Optional[tp.Group] = None
        self.launcher: Optional[tp.Loop] = None

        self.group_draw: Optional[tp.Group] = None
        self.group_simulation: Optional[tp.Group] = None
        self.group_ext: Optional[tp.Group] = None

        self.checkbox_gravity: Optional[tp.Checkbox] = None
        self.checkbox_obj_as_points: Optional[tp.Checkbox] = None

        self.helpers: list[tp.Helper] = []
        self.on_init()

    def on_init(self):
        tp.init(self.screen, theme=tp.theme_text_dark)
        tp.set_default_font(font_name="console", font_size=12)
        ico_paths = [
            "app/assets/icons/line.svg",
            "app/assets/icons/rectangle.svg",
            "app/assets/icons/circle.svg",
            "app/assets/icons/triangle.svg",
            "app/assets/icons/rubber.svg",
        ]

        draw_labels = [
            "Line",
            "Rectangle",
            "Circle",
            "Triangle",
            "Rubber",
        ]

        draw_buttons = []
        for icon_path, label in zip(ico_paths, draw_labels):
            my_img = pygame.image.load(icon_path)
            my_img = pygame.transform.smoothscale(my_img, (30, 30))
            variant = tp.graphics.change_color_on_img(
                my_img, my_img.get_at((0, 0)), (100, 100, 100)
            )
            btn = tp.ImageButton("", my_img.copy(), img_hover=variant)
            helper = tp.Helper(label, btn, countdown=30, offset=(0, 40))
            helper.set_font_size(12)
            self.helpers.append(helper)
            draw_buttons.append(btn)

        self.group_draw = tp.Group(draw_buttons, "h")

        # ================================

        sim_icons = [
            "app/assets/icons/play.svg",
            "app/assets/icons/check_point.svg",
            "app/assets/icons/vector-two-fill.svg",
        ]
        sim_labels = ["Start/Pause simulation", "Add check point", "Simulation Space"]

        sim_buttons = []
        for icon_path, label in zip(sim_icons, sim_labels):
            my_img = pygame.image.load(icon_path)
            my_img = pygame.transform.smoothscale(my_img, (30, 30))
            variant = tp.graphics.change_color_on_img(
                my_img, my_img.get_at((0, 0)), (100, 100, 100)
            )
            btn = tp.ImageButton("", my_img.copy(), img_hover=variant)
            helper = tp.Helper(label, btn, countdown=30, offset=(0, 40))
            helper.set_font_size(12)
            self.helpers.append(helper)
            sim_buttons.append(btn)

        self.group_simulation = tp.Group(sim_buttons, "h")
        # ================================
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

        # ================================

        self.metagroup = tp.Group(
            [self.group_draw, self.group_simulation, self.group_ext]
        )
        self.metagroup.sort_children("h", gap=30)
        self.metagroup.set_size(self.screen.get_size())
        self.metagroup.set_topleft(0, 10)
        self.launcher = self.metagroup.get_updater()

    def render(self):
        self.screen.fill((30, 30, 30))
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
