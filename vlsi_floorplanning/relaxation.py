"""Overlap relaxation for initial floor-plans."""

from __future__ import annotations

import math

from .cost import count_overlaps, pair_overlap_area
from .models import Floorplan, Module


def _push_pair(first: Module, second: Module, bound_width: float, bound_height: float) -> None:
    overlap = pair_overlap_area(first, second)
    if overlap <= 0.0:
        return

    overlap_width = min(first.right, second.right) - max(first.x, second.x)
    overlap_height = min(first.bottom, second.bottom) - max(first.y, second.y)
    first_center_x = first.x + first.width / 2.0
    second_center_x = second.x + second.width / 2.0
    first_center_y = first.y + first.height / 2.0
    second_center_y = second.y + second.height / 2.0

    if overlap_width <= overlap_height:
        direction = -1.0 if first_center_x <= second_center_x else 1.0
        shift = overlap_width / 2.0 + 1.0
        first.x += direction * shift
        second.x -= direction * shift
    else:
        direction = -1.0 if first_center_y <= second_center_y else 1.0
        shift = overlap_height / 2.0 + 1.0
        first.y += direction * shift
        second.y -= direction * shift

    first.clamp_to_bounds(bound_width, bound_height)
    second.clamp_to_bounds(bound_width, bound_height)


def relax_floorplan(floorplan: Floorplan, max_passes: int = 80) -> Floorplan:
    """Separate overlapping modules with small pairwise repulsive moves."""

    relaxed = floorplan.clone()
    if not relaxed.modules:
        return relaxed

    previous_overlaps = math.inf
    stagnant_passes = 0
    for _ in range(max_passes):
        modules = relaxed.modules
        for index, first in enumerate(modules):
            for second in modules[index + 1 :]:
                _push_pair(first, second, relaxed.bound_width, relaxed.bound_height)
        relaxed.clamp_modules()
        current_overlaps = count_overlaps(relaxed)
        if current_overlaps == 0:
            break
        if current_overlaps >= previous_overlaps:
            stagnant_passes += 1
        else:
            stagnant_passes = 0
        previous_overlaps = current_overlaps
        if stagnant_passes >= 12:
            break
    return relaxed
