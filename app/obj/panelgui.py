from typing import Optional

import pygame
import thorpy as tp
from obj.drawassistance import DrawAssistance
from obj.guielements.colorpalette import ColorPalette
from obj.guielements.numinputoncheckbox import NumberInputOnCheckbox
from obj.guielements.stoper import Stoper
from obj.guielements.timer import Timer
from obj.guielements.toggleimagebutton import ToggleImageButton
from obj.objectsmanager import ObjectsManager
from obj.savemanager import SaveManager


class Panel_GUI:
    def __init__(
        self,
        objectsmanager: ObjectsManager,
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

        self.objectsmanager = objectsmanager
        self.draw_assistance = draw_assistance
        self.button_play: ToggleImageButton
        self.is_rubber_on: bool = False
        self.save_manager = SaveManager()
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
            img = pygame.transform.smoothscale(img, (25, 25))
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
            img = pygame.transform.smoothscale(img, (25, 25))
            variant = tp.graphics.change_color_on_img(
                img, img.get_at((0, 0)), (100, 100, 100)
            )

            # --- Play/Stop ---
            if "play.svg" in icon_path:
                # --- Wczytanie ikon ---
                img_play = pygame.image.load("app/assets/icons/play.svg")
                img_play = pygame.transform.smoothscale(img_play, (25, 25))
                img_play_hover = tp.graphics.change_color_on_img(
                    img_play, img_play.get_at((0, 0)), (100, 100, 100)
                )

                img_stop = pygame.image.load("app/assets/icons/stop.svg")
                img_stop = pygame.transform.smoothscale(img_stop, (25, 25))
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
                    on_toggle=self.objectsmanager.run_simulation,
                )
                btn = self.button_play
            else:
                btn = tp.ImageButton("", img.copy(), img_hover=variant)
            if label == "Reset":
                btn._at_click = self.objectsmanager.reset_simulation
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
            input_text="9.81 ",
            fun=self.objectsmanager.set_gravity_force,
            input_placeholder="9.81 ",
        )
        self.stop_simulation_at_collision = tp.Checkbox()

        group = tp.Group(
            [
                self.stop_simulation_at_collision,
                tp.Text("Stop simulation at collision", font_size=14),
            ],
            'h',
        )
        self.group_ext = tp.Group(
            [self.gravity_input.get(), group], "v", gap=5, align="left"
        )
        # --- Color Palette ---
        self.color_palette = ColorPalette()
        self.group_color = self.color_palette.get()
        # --- Save ---
        img = pygame.image.load("app/assets/icons/save.svg")
        img = pygame.transform.smoothscale(img, (25, 25))
        variant = tp.graphics.change_color_on_img(
            img, img.get_at((0, 0)), (100, 100, 100)
        )
        btn_save = tp.ImageButton("", img.copy(), img_hover=variant)
        helper = tp.Helper('Save', btn_save, countdown=30, offset=(0, 40))
        helper.set_font_size(12)

        def on_save():
            data = self.objectsmanager.transfer_to_json()
            save_dir = "./app/local_save"
            self.save_manager.save_to_json(data, save_dir)

        btn_save.default_at_unclick = on_save
        # -- Load ---
        img = pygame.image.load("app/assets/icons/load.svg")
        img = pygame.transform.smoothscale(img, (25, 25))
        variant = tp.graphics.change_color_on_img(
            img, img.get_at((0, 0)), (100, 100, 100)
        )
        btn_load = tp.ImageButton("", img.copy(), img_hover=variant)
        helper = tp.Helper('Load file', btn_load, countdown=30, offset=(0, 40))
        helper.set_font_size(12)

        def on_load():
            save_dir = "./app/local_save"
            data = self.save_manager.load_from_json(save_dir)
            if data:
                self.gravity_input.input.value = str(round(data.get("gravity")[1], 4))
                self.objectsmanager.load_from_json(data)
                self.objectsmanager.reset_simulation()
                if self.stoper:
                    self.stoper.display.set_value(
                        self.stoper._prep_text(self.stoper.value)
                    )

        btn_load.default_at_unclick = on_load
        save_group = tp.Group([btn_save, btn_load], 'h', gap=10)
        # --- Clear Btn ---
        img = pygame.image.load("app/assets/icons/clear.svg")
        img = pygame.transform.smoothscale(img, (25, 25))
        variant = tp.graphics.change_color_on_img(
            img, img.get_at((0, 0)), (100, 100, 100)
        )
        btn_clr = tp.ImageButton("", img.copy(), img_hover=variant)
        helper = tp.Helper('Clear', btn_clr, countdown=30, offset=(0, 40))
        helper.set_font_size(12)

        def clear_all():
            for obj in self.objectsmanager.objects:
                obj.destroy()
            self.objectsmanager.objects.clear()
            self.objectsmanager.reset_simulation()

        btn_clr.default_at_unclick = clear_all
        # --- Info ---
        img = pygame.image.load("app/assets/icons/info.svg")
        img = pygame.transform.smoothscale(img, (25, 25))
        variant = tp.graphics.change_color_on_img(
            img, img.get_at((0, 0)), (100, 100, 100)
        )
        btn_info = tp.ImageButton("", img.copy(), img_hover=variant)
        helper = tp.Helper('Load file', btn_info, countdown=30, offset=(0, 40))
        helper.set_font_size(12)

        text = """
        position - meters (m)
        velocity - meters per second (m/s)
        force - newtons (N)
        mass - kilograms (kg)
        density - kilograms per square meter (kg/m²) - in 2D
        gravity - meters per second squared (m/s²)
        angular velocity - radians per second (rad/s)
        friction - unitless coefficient
        restitution - unitless coefficient
        """

        info_view = tp.Alert("Quantities and measurement units", text, ok_text="Close")

        def show_info():
            info_view.launch_alone(click_outside_cancel=True)

        btn_info.default_at_unclick = show_info
        # ------
        self.simulation_timer = Timer(self.objectsmanager)
        self.stoper = Stoper()
        # ------
        self.metagroup = tp.Group(
            [
                self.group_draw,
                self.group_simulation,
                self.group_ext,
                self.group_color,
                save_group,
                tp.Group([btn_clr, btn_info], "h"),
                self.simulation_timer.get(),
                self.stoper.get(),
            ]
        )
        self.metagroup.sort_children("h", gap=6)
        self.metagroup.set_size(self.screen.get_size())
        self.mainbox = tp.Box([self.metagroup])
        self.mainbox.set_topleft(0, 0)
        self.mainbox.set_bck_color((0, 0, 0))

    def after_update(self):
        self.draw_assistance.set_color(self.color_palette.selected_color)
        self.color_palette.update_color_preview()
        self.simulation_timer.update()
        self.objectsmanager.stop_simulation_at_collision = (
            self.stop_simulation_at_collision.value
        )

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
