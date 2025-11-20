import pygame
import thorpy as tp


class ColorPalette:
    def __init__(self):
        self.selected_color = pygame.Vector3(255, 255, 255)

        self.picker_predef = tp.ColorPickerPredefined(
            [
                pygame.Vector3(255, 255, 255),
                pygame.Vector3(255, 80, 80),
                pygame.Vector3(255, 165, 0),
                pygame.Vector3(255, 246, 143),
                pygame.Vector3(80, 255, 80),
                pygame.Vector3(150, 150, 255),
            ],
            nx=3,
            ny=2,
            col_size=(20, 20),
        )

        # obraz podglądu koloru
        self.color_surface = pygame.Surface((30, 30))
        self.color_surface.fill(self.selected_color)
        self.color_preview = tp.Image(self.color_surface)
        helper = tp.Helper('Color Palette', self.color_preview, offset=(-20, 42))
        helper.set_font_size(12)
        self.group_color = tp.Group(
            [self.color_preview, self.picker_predef], "h", gap=3
        )

    def update_color_preview(self):
        """Sprawdza czy kolor się zmienił i aktualizuje podgląd."""
        current = self.picker_predef.get_value()
        if current != self.selected_color:
            self.selected_color = current
            self.color_surface.fill(current)
            self.color_preview._img = self.color_surface
            self.color_preview.refresh_surfaces_build()

    def get(self):
        return self.group_color
