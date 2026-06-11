"""Cost and geometry utilities for rectangular floor-plans."""

from __future__ import annotations

from .models import AnnealingConfig, Floorplan, Module


def calculate_used_area(floorplan: Floorplan) -> float:
    if not floorplan.modules:
        return 0.0
    min_x = min(module.x for module in floorplan.modules)
    min_y = min(module.y for module in floorplan.modules)
    max_x = max(module.right for module in floorplan.modules)
    max_y = max(module.bottom for module in floorplan.modules)
    return max(0.0, max_x - min_x) * max(0.0, max_y - min_y)


def pair_overlap_area(first: Module, second: Module) -> float:
    overlap_width = max(0.0, min(first.right, second.right) - max(first.x, second.x))
    overlap_height = max(0.0, min(first.bottom, second.bottom) - max(first.y, second.y))
    return overlap_width * overlap_height


def calculate_overlap_area(floorplan: Floorplan) -> float:
    total = 0.0
    modules = floorplan.modules
    for index, first in enumerate(modules):
        for second in modules[index + 1 :]:
            total += pair_overlap_area(first, second)
    return total


def count_overlaps(floorplan: Floorplan) -> int:
    total = 0
    modules = floorplan.modules
    for index, first in enumerate(modules):
        for second in modules[index + 1 :]:
            if pair_overlap_area(first, second) > 0.0:
                total += 1
    return total


def calculate_out_of_bounds_area(floorplan: Floorplan) -> float:
    total = 0.0
    for module in floorplan.modules:
        left = max(0.0, -module.x)
        top = max(0.0, -module.y)
        right = max(0.0, module.right - floorplan.bound_width)
        bottom = max(0.0, module.bottom - floorplan.bound_height)

        horizontal_out = min(module.width, left + right)
        vertical_out = min(module.height, top + bottom)
        total += horizontal_out * module.height
        total += vertical_out * module.width
        total -= horizontal_out * vertical_out
    return max(0.0, total)


def calculate_boundary_penalty(
    floorplan: Floorplan, boundary_penalty_factor: float = 10000.0
) -> float:
    return calculate_out_of_bounds_area(floorplan) * boundary_penalty_factor


def calculate_cost(floorplan: Floorplan, config: AnnealingConfig) -> float:
    used_area = calculate_used_area(floorplan)
    overlap_area = calculate_overlap_area(floorplan)
    out_of_bounds_area = calculate_out_of_bounds_area(floorplan)
    dead_space = max(0.0, used_area - floorplan.total_module_area)
    return (
        used_area
        + overlap_area * config.overlap_penalty_factor
        + out_of_bounds_area * config.boundary_penalty_factor
        + config.dead_space_weight * dead_space
    )


def collect_metrics(floorplan: Floorplan, config: AnnealingConfig) -> dict[str, float]:
    used_area = calculate_used_area(floorplan)
    overlap_area = calculate_overlap_area(floorplan)
    out_of_bounds_area = calculate_out_of_bounds_area(floorplan)
    dead_space = max(0.0, used_area - floorplan.total_module_area)
    return {
        "usedArea": used_area,
        "totalModuleArea": floorplan.total_module_area,
        "deadSpace": dead_space,
        "overlapArea": overlap_area,
        "outOfBoundsArea": out_of_bounds_area,
        "boundingArea": floorplan.bounding_area,
        "cost": calculate_cost(floorplan, config),
    }
