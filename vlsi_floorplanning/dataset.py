"""Example modules inspired by the referenced VLSI floor-planning paper."""

from __future__ import annotations

from .models import Module


def create_example_modules(rotatable: bool = True) -> list[Module]:
    return [
        Module("A", 40, 50, rotatable=rotatable),
        Module("B", 75, 50, rotatable=rotatable),
        Module("C", 85, 60, rotatable=rotatable),
        Module("D", 100, 30, rotatable=rotatable),
        Module("E", 100, 50, rotatable=rotatable),
        Module("F", 75, 45, rotatable=rotatable),
        Module("G", 60, 27, rotatable=rotatable),
        Module("H", 80, 40, rotatable=rotatable),
        Module("I", 30, 45, rotatable=rotatable),
        Module("J", 75, 45, rotatable=rotatable),
    ]
