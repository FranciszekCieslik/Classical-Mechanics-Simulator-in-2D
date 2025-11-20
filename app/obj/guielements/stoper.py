import pygame
import thorpy as tp


class Stoper:
    def __init__(self) -> None:
        self.value: int = 0
        # --- Btn-Up ---
        img = pygame.image.load("app/assets/icons/arrow-up.svg")
        img = pygame.transform.smoothscale(img, (25, 25))
        variant = tp.graphics.change_color_on_img(
            img, img.get_at((0, 0)), (100, 100, 100)
        )
        self.btn_up = tp.ImageButton("", img.copy(), img_hover=variant)
        self.btn_up.default_at_unclick = self._val_up
        # --- Btn-Down ---
        img = pygame.image.load("app/assets/icons/arrow-down.svg")
        img = pygame.transform.smoothscale(img, (25, 25))
        variant = tp.graphics.change_color_on_img(
            img, img.get_at((0, 0)), (100, 100, 100)
        )
        self.btn_down = tp.ImageButton("", img.copy(), img_hover=variant)
        self.btn_down.default_at_unclick = self._val_down
        # ---
        self.display = tp.Text('00s', font_size=14)
        helper = tp.Helper('Stop at', self.display, offset=(0, 42))
        helper.set_font_size(12)

        self.metagroup = tp.Group([self.btn_up, self.display, self.btn_down], gap=2)

    def _prep_text(self, val: int) -> str:
        res = ''
        if val < 10:
            res = '0'
        res = res + str(val) + 's'
        return res

    def get(self):
        return self.metagroup

    def _val_up(self) -> None:
        self.value += 1
        txt = self._prep_text(self.value)
        self.display.set_value(txt)

    def _val_down(self) -> None:
        if self.value == 0:
            return
        self.value -= 1
        txt = self._prep_text(self.value)
        self.display.set_value(txt)
