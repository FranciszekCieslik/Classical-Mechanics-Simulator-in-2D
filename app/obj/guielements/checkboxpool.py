from typing import Callable, Optional

import thorpy as tp


class CheckboxPool:
    def __init__(self, choices: list[str], fun: Callable, mode: str = "h"):
        self.choices = choices
        self._callback = fun
        self.checkboxes: list[tp.Checkbox] = []
        self.selected = choices[0]
        self.prev_state: list[bool] = []
        elements = []
        for c in choices:
            checkbox = tp.Checkbox()
            self.checkboxes.append(checkbox)
            group = tp.Group([tp.Text(c, font_size=14), checkbox], "h")
            elements.append(group)
            self.prev_state.append(False)
        self.checkboxes[0].value = True
        self.prev_state[0] = True
        self.main_group = tp.Group(elements, mode)

    def get(self):
        return self.main_group

    def get_value(self):
        return self.selected

    def toggle(self):
        state = [c.value for c in self.checkboxes]
        if state == self.prev_state:
            return

        clicked_idx = None
        for i, (s, ps) in enumerate(zip(state, self.prev_state)):
            if s != ps:
                clicked_idx = i
                break

        if clicked_idx is None:
            return

        if self.prev_state[clicked_idx]:
            self.checkboxes[clicked_idx].set_value(True)
            return

        for i, cb in enumerate(self.checkboxes):
            cb.set_value(i == clicked_idx)

        self.selected = self.choices[clicked_idx]
        self.prev_state = [cb.value for cb in self.checkboxes]
        self._callback()
