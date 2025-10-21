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
        self.group_views: Optional[tp.Group] = None
        self.group_ext: Optional[tp.Group] = None

        self.checkbox_gravity: Optional[tp.Checkbox] = None
        self.input_gravity: Optional[tp.Checkbox] = None

        self.helpers: list[tp.Helper] = []
        self.on_init()

    def on_init(self):
        tp.init(self.screen, theme=tp.theme_text_dark)

        # icons_path = [
        #     "app/assets/icons/line.svg",
        #     "app/assets/icons/rectangle.svg",
        #     "app/assets/icons/circle.svg",
        #     "app/assets/icons/triangle.svg",
        #     "app/assets/icons/rubber.svg",
        # ]
        # draw_labels = [
        #     "Line tool",
        #     "Rectangle tool",
        #     "Circle tool",
        #     "Triangle tool",
        #     "Rubber",
        # ]

        # draw_buttons = []
        # for icon, label in zip(icons_path, draw_labels):
        #     ico = pygame.image.load(icon).convert_alpha()
        #     ico.set_colorkey(ico.get_at((0, 0)))
        #     pure_ico = tp.Image(ico)
        #     pure_ico.set_size((20, 20))

        #     variant = tp.graphics.change_color_on_img(
        #         ico, ico.get_at((50, 25)), (200, 200, 255)
        #     )
        #     variant.set_colorkey(variant.get_at((0, 0)))

        #     btn = tp.ImageButton("", ico.copy(), img_hover=variant)
        #     helper = tp.Helper(label, btn, countdown=30)
        #     self.helpers.append(helper)
        #     draw_buttons.append(btn)

        # self.group_draw = tp.Group(draw_buttons, "h")

        # ================================

        sim_icons = ["", "", "", ""]
        sim_labels = ["Start simulation", "Pause", "Stop", "Restart"]

        sim_buttons = []

        for icon, label in zip(sim_icons, sim_labels):
            btn = tp.Button(icon)
            helper = tp.Helper(label, btn, countdown=30)
            self.helpers.append(helper)
            sim_buttons.append(btn)

        # ================================

        self.group_simulation = tp.Group(sim_buttons, "h")
        self.checkbox_grid = tp.Checkbox()
        self.checkbox_vectors = tp.Checkbox()
        self.group_views = tp.Group([self.checkbox_grid, self.checkbox_vectors], "v")
        self.checkbox_gravity = tp.Checkbox()

        self.checkbox_points = tp.Checkbox()

        self.group_ext = tp.Group([self.checkbox_points])
        self.group_ext.sort_children("v")

        # ================================

        self.metagroup = tp.Group(
            [self.group_simulation, self.group_views, self.group_ext]
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
