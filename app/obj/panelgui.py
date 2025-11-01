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
        self.group_color: Optional[tp.Group] = None

        self.checkbox_gravity: Optional[tp.Checkbox] = None
        self.checkbox_obj_as_points: Optional[tp.Checkbox] = None

        self.helpers: list[tp.Helper] = []

        # Callback zewnętrzny (np. App.toggle_simulation)
        self.toggle_simulation = lambda: None
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
            helper = tp.Helper(label, btn, countdown=30, offset=(0, 40))
            helper.set_font_size(12)
            self.helpers.append(helper)
            draw_buttons.append(btn)
        self.group_draw = tp.Group(draw_buttons, "h")

        # === Przyciski symulacji (Play/Stop + inne) ===
        sim_icons = [
            "app/assets/icons/play.svg",
            "app/assets/icons/check_point.svg",
            "app/assets/icons/vector-two-fill.svg",
        ]
        sim_labels = ["Start/Pause simulation", "Add check point", "Simulation Space"]

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

                # --- Tworzenie przycisku ---
                self.button_play = tp.ImageButton(
                    "", img_play.copy(), img_hover=img_play_hover
                )
                self.button_play.playing = False  # stan początkowy

                def toggle_play():
                    # Przełącz stan
                    self.button_play.playing = not self.button_play.playing

                    if self.button_play.playing:
                        # Zmień na ikonę stop
                        self.button_play.img = img_stop.copy()
                        self.button_play.img_hover = img_stop_hover
                        self.button_play.generate_surfaces()
                    else:
                        # Zmień na ikonę play
                        self.button_play.img = img_play.copy()
                        self.button_play.img_hover = img_play_hover
                        self.button_play.generate_surfaces()

                    # Odśwież obrazek na przycisku
                    self.button_play.blit_img = self.button_play.img.copy()

                    # Wywołaj callback zewnętrzny
                    self.toggle_simulation(self.button_play.playing)

                self.button_play._at_click = toggle_play
                btn = self.button_play

            else:
                btn = tp.ImageButton("", img.copy(), img_hover=variant)
                helper = tp.Helper(label, btn, countdown=30, offset=(0, 40))
                helper.set_font_size(12)
                self.helpers.append(helper)

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
