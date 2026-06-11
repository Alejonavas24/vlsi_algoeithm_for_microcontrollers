"""Experiment orchestration for module-order floor-planning studies."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from .annealing import simulated_annealing
from .cost import calculate_out_of_bounds_area, calculate_used_area
from .models import AnnealingConfig, AnnealingResult, Floorplan, Module
from .relaxation import relax_floorplan


@dataclass
class ExperimentResult:
    results: list[AnnealingResult]
    best_result: AnnealingResult

    def table_rows(self) -> list[dict[str, float | int | str]]:
        rows: list[dict[str, float | int | str]] = []
        for result in self.results:
            rows.append(
                {
                    "configuration": result.configuration_name,
                    "initialArea": round(result.initial_area, 2),
                    "finalArea": round(result.final_area, 2),
                    "improvementPercent": round(result.improvement_percent, 2),
                    "finalCost": round(result.final_cost, 2),
                    "finalOverlaps": result.final_overlaps,
                }
            )
        return rows

    def to_dict(self) -> dict[str, object]:
        return {
            "bestConfiguration": self.best_result.configuration_name,
            "initialArea": round(self.best_result.initial_area, 4),
            "finalArea": round(self.best_result.final_area, 4),
            "improvementPercent": round(self.best_result.improvement_percent, 4),
            "modules": [
                module.to_dict() for module in self.best_result.final_floorplan.modules
            ],
            "metrics": self.best_result.metrics,
            "history": {
                result.configuration_name: result.history for result in self.results
            },
            "results": [result.to_dict() for result in self.results],
        }


def calculate_bounding_rectangle(modules: list[Module]) -> tuple[float, float]:
    lower_bound_area = sum(module.area for module in modules)
    target_area = lower_bound_area * 1.5
    max_width = max(module.width for module in modules)
    max_height = max(module.height for module in modules)
    width = max(max_width, math.sqrt(target_area) * 1.08)
    height = max(max_height, target_area / width)
    return math.ceil(width), math.ceil(height)


def create_initial_floorplan(
    configuration_name: str,
    ordered_modules: list[Module],
    bound_width: float,
    bound_height: float,
) -> Floorplan:
    modules = [Module(module.id, module.width, module.height, rotatable=module.rotatable) for module in ordered_modules]
    x_cursor = 0.0
    y_cursor = 0.0
    row_height = 0.0
    gap = 2.0

    for module in modules:
        if x_cursor > 0.0 and x_cursor + module.width > bound_width:
            x_cursor = 0.0
            y_cursor += row_height + gap
            row_height = 0.0
        if y_cursor + module.height > bound_height:
            module.x = max(0.0, bound_width - module.width)
            module.y = max(0.0, bound_height - module.height)
        else:
            module.x = x_cursor
            module.y = y_cursor
        x_cursor += module.width + gap
        row_height = max(row_height, module.height)

    floorplan = Floorplan(modules, bound_width, bound_height, name=configuration_name)
    floorplan.clamp_modules()
    return floorplan


def _swap_by_id(modules: list[Module], first_id: str, second_id: str) -> list[Module]:
    swapped = list(modules)
    first_index = next(index for index, module in enumerate(swapped) if module.id == first_id)
    second_index = next(index for index, module in enumerate(swapped) if module.id == second_id)
    swapped[first_index], swapped[second_index] = swapped[second_index], swapped[first_index]
    return swapped


def generate_initial_orders(modules: list[Module]) -> dict[str, list[Module]]:
    rng_fp2 = random.Random(2)
    fp2 = list(modules)
    rng_fp2.shuffle(fp2)

    fp3 = sorted(modules, key=lambda module: module.area, reverse=True)
    fp4 = _swap_by_id(modules, "J", "H")
    fp5 = _swap_by_id(modules, "A", "H")

    fp6 = list(modules)
    rng_fp6 = random.Random(6)
    for _ in range(max(4, len(fp6))):
        first_index, second_index = rng_fp6.sample(range(len(fp6)), 2)
        fp6[first_index], fp6[second_index] = fp6[second_index], fp6[first_index]

    return {
        "FP_1": list(modules),
        "FP_2": fp2,
        "FP_3": fp3,
        "FP_4": fp4,
        "FP_5": fp5,
        "FP_6": fp6,
    }


def choose_best_result(results: list[AnnealingResult]) -> AnnealingResult:
    valid = [
        result
        for result in results
        if result.final_overlaps == 0
        and calculate_out_of_bounds_area(result.final_floorplan) == 0.0
    ]
    candidates = valid if valid else results
    return min(
        candidates,
        key=lambda result: (
            result.final_overlaps,
            calculate_out_of_bounds_area(result.final_floorplan),
            result.final_area,
            result.final_cost,
        ),
    )


def run_module_order_experiment(
    modules: list[Module],
    config: AnnealingConfig | None = None,
) -> ExperimentResult:
    config = config or AnnealingConfig()
    bound_width, bound_height = calculate_bounding_rectangle(modules)
    orders = generate_initial_orders(modules)
    results: list[AnnealingResult] = []

    for name, ordered_modules in orders.items():
        initial = create_initial_floorplan(name, ordered_modules, bound_width, bound_height)
        relaxed = relax_floorplan(initial)
        result = simulated_annealing(name, initial, relaxed, config)
        result.metrics["relaxedArea"] = calculate_used_area(relaxed)
        results.append(result)

    return ExperimentResult(results=results, best_result=choose_best_result(results))
