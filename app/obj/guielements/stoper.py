import pygame
import thorpy as tp


class Stoper:
    def __init__(self) -> None:
        self.value: float = 0.00
        # --- Btn-Up ---
        img = pygame.image.load("app/assets/icons/arrow-up.svg")
        img = pygame.transform.smoothscale(img, (25, 25))
        variant = tp.graphics.change_color_on_img(
            img, img.get_at((0, 0)), (100, 100, 100)
        )
        self.btn_up = tp.ImageButton("", img.copy(), img_hover=variant)
        self.btn_up.default_at_unclick = self._val_up
        # --- dcs&cs ---
        self.cs_btn_up = tp.ImageButton("", img.copy(), img_hover=variant)
        self.cs_btn_up.default_at_unclick = self._cs_val_up
        # --- Btn-Down ---
        img = pygame.image.load("app/assets/icons/arrow-down.svg")
        img = pygame.transform.smoothscale(img, (25, 25))
        variant = tp.graphics.change_color_on_img(
            img, img.get_at((0, 0)), (100, 100, 100)
        )
        self.btn_down = tp.ImageButton("", img.copy(), img_hover=variant)
        self.btn_down.default_at_unclick = self._val_down
        # --- dcs&cs ---
        self.cs_btn_down = tp.ImageButton("", img.copy(), img_hover=variant)
        self.cs_btn_down.default_at_unclick = self._cs_val_down
        # ---
        self.display = tp.Text('00.00s', font_size=14)
        helper = tp.Helper('Stop at', self.display, offset=(0, 42))
        helper.set_font_size(12)
        # --- Reset btn ---
        img = pygame.image.load("app/assets/icons/timer-reset.svg")
        img = pygame.transform.smoothscale(img, (25, 25))
        variant = tp.graphics.change_color_on_img(
            img, img.get_at((0, 0)), (100, 100, 100)
        )
        self.reset_btn = tp.ImageButton("", img.copy(), img_hover=variant)
        self.reset_btn.default_at_unclick = self._reset

        self.metagroup = tp.Group(
            [
                tp.Group(
                    [
                        tp.Group([self.btn_up, self.cs_btn_up], 'h', gap=0),
                        self.display,
                        tp.Group([self.btn_down, self.cs_btn_down], 'h', gap=0),
                    ],
                    gap=2,
                ),
                self.reset_btn,
            ],
            'h',
        )

    def _prep_text(self, val: float) -> str:
        val = round(val, 2)
        whole = int(val)
        cents = int(round((val - whole) * 100))
        return f"{whole:02d}.{cents:02d}s"

    def get(self):
        return self.metagroup

    def _val_up(self) -> None:
        self.value += 1
        txt = self._prep_text(self.value)
        self.display.set_value(txt)

    def _val_down(self) -> None:
        if self.value <= 1:
            self.value = 0
        else:
            self.value -= 1
        txt = self._prep_text(self.value)
        self.display.set_value(txt)

    def _cs_val_up(self) -> None:
        self.value += 0.01
        txt = self._prep_text(self.value)
        self.display.set_value(txt)

    def _cs_val_down(self) -> None:
        if self.value <= 0.00001:
            self.value = 0
            return
        self.value -= 0.01
        txt = self._prep_text(self.value)
        self.display.set_value(txt)

    def _reset(self):
        self.value = 0.00
        txt = self._prep_text(self.value)
        self.display.set_value(txt)
