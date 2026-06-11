"""Perturbations used by simulated annealing."""

from __future__ import annotations

import random

from .cost import pair_overlap_area
from .models import AnnealingConfig, Floorplan, Module


def move_random_module(floorplan: Floorplan, rng: random.Random, config: AnnealingConfig) -> None:
    module = rng.choice(floorplan.modules)
    step_x = max(1.0, floorplan.bound_width * config.move_step_ratio)
    step_y = max(1.0, floorplan.bound_height * config.move_step_ratio)
    module.x += rng.uniform(-step_x, step_x)
    module.y += rng.uniform(-step_y, step_y)
    module.clamp_to_bounds(floorplan.bound_width, floorplan.bound_height)


def swap_modules(floorplan: Floorplan, rng: random.Random) -> None:
    if len(floorplan.modules) < 2:
        return
    first, second = rng.sample(floorplan.modules, 2)
    first.x, second.x = second.x, first.x
    first.y, second.y = second.y, first.y
    first.clamp_to_bounds(floorplan.bound_width, floorplan.bound_height)
    second.clamp_to_bounds(floorplan.bound_width, floorplan.bound_height)


def rotate_module(floorplan: Floorplan, rng: random.Random) -> None:
    rotatable = [module for module in floorplan.modules if module.rotatable]
    if not rotatable:
        return
    module = rng.choice(rotatable)
    module.rotate()
    module.clamp_to_bounds(floorplan.bound_width, floorplan.bound_height)


def compact_towards_origin(floorplan: Floorplan, rng: random.Random, fraction: float = 0.08) -> None:
    ordered = sorted(floorplan.modules, key=lambda module: module.x + module.y)
    for module in ordered:
        module.x *= 1.0 - fraction * rng.uniform(0.3, 1.0)
        module.y *= 1.0 - fraction * rng.uniform(0.3, 1.0)
        module.clamp_to_bounds(floorplan.bound_width, floorplan.bound_height)


def repair_overlaps(floorplan: Floorplan, max_passes: int = 20) -> None:
    for _ in range(max_passes):
        moved = False
        modules = floorplan.modules
        for index, first in enumerate(modules):
            for second in modules[index + 1 :]:
                if pair_overlap_area(first, second) <= 0.0:
                    continue
                moved = True
                overlap_width = min(first.right, second.right) - max(first.x, second.x)
                overlap_height = min(first.bottom, second.bottom) - max(first.y, second.y)
                if overlap_width <= overlap_height:
                    if first.x <= second.x:
                        second.x += overlap_width + 1.0
                    else:
                        first.x += overlap_width + 1.0
                else:
                    if first.y <= second.y:
                        second.y += overlap_height + 1.0
                    else:
                        first.y += overlap_height + 1.0
                first.clamp_to_bounds(floorplan.bound_width, floorplan.bound_height)
                second.clamp_to_bounds(floorplan.bound_width, floorplan.bound_height)
        if not moved:
            break


def _overlaps_any(module: Module, modules: list[Module]) -> bool:
    return any(other is not module and pair_overlap_area(module, other) > 0.0 for other in modules)


def legal_compact_towards_origin(floorplan: Floorplan, passes: int = 3) -> None:
    """Greedily move modules left/up while preserving non-overlap."""

    floorplan.clamp_modules()
    for _ in range(passes):
        for module in sorted(floorplan.modules, key=lambda item: (item.y, item.x)):
            original_x = module.x
            low = 0.0
            high = module.x
            for _ in range(18):
                mid = (low + high) / 2.0
                module.x = mid
                if _overlaps_any(module, floorplan.modules):
                    low = mid
                else:
                    high = mid
            module.x = high
            if _overlaps_any(module, floorplan.modules):
                module.x = original_x

            original_y = module.y
            low = 0.0
            high = module.y
            for _ in range(18):
                mid = (low + high) / 2.0
                module.y = mid
                if _overlaps_any(module, floorplan.modules):
                    low = mid
                else:
                    high = mid
            module.y = high
            if _overlaps_any(module, floorplan.modules):
                module.y = original_y
        floorplan.clamp_modules()


def perturb_solution(
    floorplan: Floorplan,
    rng: random.Random,
    config: AnnealingConfig,
    repair_probability: float = 0.35,
) -> str:
    move = rng.choices(
        ["move", "swap", "rotate", "compact"],
        weights=[0.45, 0.20, 0.20, 0.15],
        k=1,
    )[0]
    if move == "move":
        move_random_module(floorplan, rng, config)
    elif move == "swap":
        swap_modules(floorplan, rng)
    elif move == "rotate":
        rotate_module(floorplan, rng)
    else:
        compact_towards_origin(floorplan, rng)

    floorplan.clamp_modules()
    if rng.random() < repair_probability:
        repair_overlaps(floorplan)
    return move
