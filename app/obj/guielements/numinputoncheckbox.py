from typing import Callable

import thorpy as tp


class NumberInputOnCheckbox:
    def __init__(
        self,
        checkbox_text: str,
        input_text: str,
        fun: Callable[[float], None],
        input_placeholder: str = "",
    ):
        if not callable(fun):
            raise TypeError("'fun' must be a function or lambda expression")

        self.fun = fun
        self.active = True

        self.checkbox = tp.Checkbox()
        self.checkbox.set_value(True)

        self.label_checkbox = tp.Text(checkbox_text, font_size=12)

        self.input = tp.TextInput(input_text, input_placeholder)
        self.input.set_size((120, 28))
        self.input.set_only_numbers()
        self._set_input_visual(active=True)

        self.group = tp.Group([self.checkbox, self.label_checkbox, self.input], "h")

        self.checkbox._at_click = self.on_checkbox_toggle
        self.input.at_cancel = self.on_input_entered

    def _set_input_visual(self, active: bool):
        color = (80, 80, 80) if active else (150, 150, 150)
        self.input.set_bck_color(color)
        self.active = active

    def on_checkbox_toggle(self):
        """Zmieniaj stan logiczny pola przy zmianie checkboxa."""
        active = not self.checkbox.get_value()
        self._set_input_visual(active=active)
        self.input.set_locked(not active)

    def on_input_entered(self):
        text = self.input.get_value().strip()
        if not text:
            return

        try:
            val = float(text)
        except ValueError:
            self.input.set_value("")
            return

        try:
            self.fun(val)
        except Exception as e:
            print(f"{e}")

    def get(self) -> tp.Group:
        """Zwraca grupę GUI do wstawienia do menu Thorpy."""
        return self.group
