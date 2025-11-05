import thorpy as tp


class ToggleImageButton(tp.ImageButton):
    """Image button that behaves like a toggle (stays pressed until clicked again).

    Mandatory arguments:
        text : string to display on the image (can be empty).
        img : pygame surface for normal state.

    Optional arguments:
        img_hover : image when mouse is over.
        img_pressed : image when clicked (toggle on).
        img_pressed_hover : image when hovered while pressed.
        img_locked : image when locked (optional).
        no_copy : if True, uses same surface for all states.
        value : initial toggle state (False=off, True=on)
        on_toggle : optional callback (value: bool) -> None
    """

    def __init__(
        self,
        text,
        img,
        img_hover=None,
        img_pressed=None,
        img_pressed_hover=None,
        img_locked=None,
        no_copy=False,
        value=False,
        on_toggle=None,
    ):
        super().__init__(text, img, img_hover, img_pressed, img_locked, no_copy)
        self.value = value
        self.on_toggle = on_toggle

        # --- Dodanie dodatkowych stanów ---
        # selected = toggle on, normal (nie hover)
        self.imgs["selected"] = self.imgs.get("pressed", self.imgs["normal"])
        self.surfaces["selected"] = self.surfaces.get(
            "pressed", self.surfaces["normal"]
        )

        if img_pressed_hover is not None:
            self.imgs["pressed_hover"] = img_pressed_hover
            self.surfaces["pressed_hover"] = [img_pressed_hover]
        else:
            self.imgs["pressed_hover"] = self.imgs["pressed"]
            self.surfaces["pressed_hover"] = self.surfaces["pressed"]

        # ustawienie funkcji wybierającej ramkę
        self.get_frame = self.get_frame_togglable
        self.action = self.default_at_unclick

    # --- toggle ---
    def toggle(self):
        self.value = not self.value
        if callable(self.on_toggle):
            self.on_toggle(self.value)

    def default_at_unclick(self):
        self.toggle()

    # --- wybór grafiki ---
    def get_frame_togglable(self, state, it):
        """Zwraca właściwy obraz w zależności od toggle i hover."""
        if self.value:  # toggle on
            if state == "hover":
                state = "pressed_hover"
            else:
                state = "selected"

        return self.surfaces[state][it]

    # --- get/set value ---
    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = value
        if callable(self.on_toggle):
            self.on_toggle(value)
