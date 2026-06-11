"""Simulated annealing optimizer for coordinate-based VLSI floor-planning."""

from __future__ import annotations

import math
import random

from .cost import calculate_cost, calculate_used_area, collect_metrics, count_overlaps
from .models import AnnealingConfig, AnnealingResult, Floorplan
from .perturbation import legal_compact_towards_origin, perturb_solution, repair_overlaps


def cool_temperature(
    initial_temperature: float,
    current_temperature: float,
    iteration: int,
    total_iterations: int,
    profile: str,
    min_temperature: float,
) -> float:
    if profile == "linear":
        decrement = (initial_temperature - min_temperature) / max(1, total_iterations)
        return max(min_temperature, current_temperature - decrement)
    if profile == "logarithmic":
        return max(min_temperature, initial_temperature / (1.0 + math.log(iteration + 2.0)))
    raise ValueError(f"Unsupported cooling profile: {profile!r}")


def should_accept(delta_cost: float, temperature: float, rng: random.Random) -> bool:
    if delta_cost <= 0.0:
        return True
    if temperature <= 0.0:
        return False
    probability = math.exp(-delta_cost / temperature)
    return rng.random() < probability


def simulated_annealing(
    configuration_name: str,
    initial_floorplan: Floorplan,
    relaxed_floorplan: Floorplan,
    config: AnnealingConfig,
) -> AnnealingResult:
    seed_offset = sum(ord(char) for char in configuration_name)
    rng = random.Random(config.random_seed + seed_offset)

    current = relaxed_floorplan.clone()
    current_cost = calculate_cost(current, config)
    best = current.clone()
    best_cost = current_cost
    history: list[dict[str, float]] = []
    temperature = config.initial_temperature

    for iteration in range(config.iterations):
        accepted_moves = 0
        for _ in range(config.moves_per_temperature):
            candidate = current.clone()
            perturb_solution(candidate, rng, config)
            new_cost = calculate_cost(candidate, config)
            delta = new_cost - current_cost
            if should_accept(delta, temperature, rng):
                current = candidate
                current_cost = new_cost
                accepted_moves += 1
                if new_cost < best_cost:
                    best = candidate.clone()
                    best_cost = new_cost
        history.append(
            {
                "iteration": iteration + 1,
                "temperature": round(temperature, 6),
                "area": round(calculate_used_area(current), 4),
                "cost": round(current_cost, 4),
                "bestArea": round(calculate_used_area(best), 4),
                "bestCost": round(best_cost, 4),
                "acceptedMoves": accepted_moves,
            }
        )
        temperature = cool_temperature(
            config.initial_temperature,
            temperature,
            iteration + 1,
            config.iterations,
            config.cooling_profile,
            config.min_temperature,
        )

    repair_overlaps(best, max_passes=80)
    legal_compact_towards_origin(best)
    best.clamp_modules()
    final_cost = calculate_cost(best, config)
    initial_area = calculate_used_area(initial_floorplan)
    final_area = calculate_used_area(best)
    improvement_percent = (
        ((initial_area - final_area) / initial_area) * 100.0 if initial_area else 0.0
    )
    return AnnealingResult(
        configuration_name=configuration_name,
        initial_floorplan=initial_floorplan.clone(),
        relaxed_floorplan=relaxed_floorplan.clone(),
        final_floorplan=best,
        initial_area=initial_area,
        final_area=final_area,
        improvement_percent=improvement_percent,
        final_cost=final_cost,
        final_overlaps=count_overlaps(best),
        history=history,
        metrics=collect_metrics(best, config),
    )
