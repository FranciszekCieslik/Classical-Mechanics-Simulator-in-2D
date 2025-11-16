import pygame
import thorpy


class NumberInput(thorpy.TextInput):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # rozszerzone flagi
        self.allow_negative = True  # pozwala na "-"
        self.allow_decimal = True  # pozwala na "."

    def set_only_non_negative(self):
        """Blokuje możliwość wpisania znaku '-'."""
        self.allow_negative = False

    def accept_char(self, char):
        """
        Akceptuje tylko cyfry, opcjonalnie '.' oraz '-' (jeśli pierwszy i nie ma go jeszcze).
        """
        # cyfry
        if char.isdigit():
            return True

        if char == "-":
            if not self.allow_negative:
                return False
            return self.cursor_pos == 0 and "-" not in self.value

        if char == ".":
            if not self.allow_decimal:
                return False
            return "." not in self.value

        return False

    def reaction_keyboard(self, e):
        if e.type == pygame.KEYDOWN:
            self.last_keydown = self.it

            if e.key in self.keys_validate:
                thorpy.loops.quit_current_loop()
                self.on_validation()
                return

            if e.key in self.keys_cancel:
                self.value = self.initial_value
                if e.key != pygame.K_ESCAPE:
                    thorpy.loops.quit_current_loop()
                return

            if e.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.value = (
                        self.value[: self.cursor_pos - 1]
                        + self.value[self.cursor_pos :]
                    )
                    self.cursor_pos -= 1
                return

            if e.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.value):
                    self.value = (
                        self.value[: self.cursor_pos]
                        + self.value[self.cursor_pos + 1 :]
                    )
                return

            if e.key == pygame.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos - 1)
                return

            if e.key == pygame.K_RIGHT:
                self.cursor_pos = min(len(self.value), self.cursor_pos + 1)
                return

            if len(self.value) < self.max_length:
                if e.unicode and ord(e.unicode) > 31:
                    if self.accept_char(e.unicode):
                        self.value = (
                            self.value[: self.cursor_pos]
                            + e.unicode
                            + self.value[self.cursor_pos :]
                        )
                        self.cursor_pos += 1
