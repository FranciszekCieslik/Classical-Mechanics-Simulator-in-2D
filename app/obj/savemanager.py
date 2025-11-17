import json
import os
from tkinter import filedialog as fd
from typing import Any

import pygame
import thorpy as tp


def to_json_safe(value):
    # pygame.Vector2
    if isinstance(value, pygame.Vector2):
        return [value.x, value.y]

    # pygame.Vector3
    if isinstance(value, pygame.Vector3):
        return [value.x, value.y, value.z]

    # tuple -> list
    if isinstance(value, tuple):
        return [to_json_safe(v) for v in value]

    # list -> list
    if isinstance(value, list):
        return [to_json_safe(v) for v in value]

    # dict -> dict
    if isinstance(value, dict):
        return {k: to_json_safe(v) for k, v in value.items()}

    # everything else remain unchanged (int, float, str, bool, None)
    return value


class SaveManager:
    def __init__(self):
        self.tk_dialog = fd.asksaveasfilename
        cls_text = tp.Text
        self.initial_value = 'autosave.json'
        self.tk_dialog_value = cls_text('autosave.json')
        self.tk_dialog_value.hand_cursor = True
        self.basename = True
        self.extension = True
        self.filetypes = [("JSON files", ".json")]
        self.initial_dir = "./app/local_save"

    def save_at_unclick(self):
        self.tk_dialog = fd.asksaveasfilename
        if self.filetypes:
            try:
                value = self.tk_dialog(
                    initialdir=self.initial_dir,
                    filetypes=self.filetypes,
                    initialfile=self.initial_value,
                )
            except:
                value = self.tk_dialog(
                    initialdir=self.initial_dir, filetypes=self.filetypes
                )
        else:
            try:
                value = self.tk_dialog(
                    initialdir=self.initial_dir, initialfile=self.initial_value
                )
            except:
                value = self.tk_dialog(initialdir=self.initial_dir)
        if not (isinstance(value, str)):
            value = [self.clean_value(v) for v in value]
            value = "\n".join(value)
        else:
            value = self.clean_value(value)
        self.tk_dialog_value.set_text(value)

    def load_at_unclick(self):
        self.tk_dialog = fd.askopenfilename
        if self.filetypes:
            try:
                value = self.tk_dialog(
                    initialdir=self.initial_dir,
                    filetypes=self.filetypes,
                    initialfile=self.initial_value,
                )
            except:
                value = self.tk_dialog(
                    initialdir=self.initial_dir, filetypes=self.filetypes
                )
        else:
            try:
                value = self.tk_dialog(
                    initialdir=self.initial_dir, initialfile=self.initial_value
                )
            except:
                value = self.tk_dialog(initialdir=self.initial_dir)
        if not (isinstance(value, str)):
            value = [self.clean_value(v) for v in value]
            value = "\n".join(value)
        else:
            value = self.clean_value(value)
        self.tk_dialog_value.set_text(value)

    def clean_value(self, value):
        if self.basename:
            value = os.path.basename(value)
        if not self.extension:
            e = value.split(".")[-1]
            value = value.replace("." + e, "")
        return value

    def get_value(self):
        return self.tk_dialog_value.get_value()

    def save_to_json(self, data: Any, save_dir: str):
        if data is None:
            return

        data = to_json_safe(data)  # <-- DODAJ TO

        self.save_at_unclick()
        file_name = self.get_value()
        if file_name:
            file_path = os.path.join(save_dir, file_name)
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)

    def load_from_json(self, save_dir: str):
        self.load_at_unclick()

        file_name = self.get_value()
        data = None

        if not file_name:
            return None

        file_path = os.path.join(save_dir, file_name)

        if not os.path.exists(file_path):
            print(f"[ERROR] Plik {file_path} nie istnieje!")
            return None

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print(f"[ERROR] Plik {file_path} zawiera uszkodzony JSON.")
        except Exception as e:
            print(f"[ERROR] Nie udało się wczytać pliku: {e}")

        return data
