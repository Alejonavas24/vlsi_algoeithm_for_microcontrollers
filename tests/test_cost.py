from vlsi_floorplanning.cost import (
    calculate_boundary_penalty,
    calculate_cost,
    calculate_overlap_area,
    calculate_used_area,
    count_overlaps,
)
from vlsi_floorplanning.models import AnnealingConfig, Floorplan, Module


def test_calculate_used_area() -> None:
    floorplan = Floorplan(
        [
            Module("A", 10, 20, x=5, y=5),
            Module("B", 15, 10, x=30, y=15),
        ],
        bound_width=100,
        bound_height=100,
    )

    assert calculate_used_area(floorplan) == 800


def test_calculate_overlap_area_and_count() -> None:
    floorplan = Floorplan(
        [
            Module("A", 10, 10, x=0, y=0),
            Module("B", 10, 10, x=5, y=5),
            Module("C", 10, 10, x=30, y=30),
        ],
        bound_width=100,
        bound_height=100,
    )

    assert calculate_overlap_area(floorplan) == 25
    assert count_overlaps(floorplan) == 1


def test_calculate_boundary_penalty() -> None:
    floorplan = Floorplan(
        [Module("A", 10, 10, x=95, y=95)],
        bound_width=100,
        bound_height=100,
    )

    assert calculate_boundary_penalty(floorplan, boundary_penalty_factor=10) == 750


def test_cost_penalizes_overlap_and_dead_space() -> None:
    config = AnnealingConfig(overlap_penalty_factor=100, dead_space_weight=0.5)
    clean = Floorplan(
        [Module("A", 10, 10, x=0, y=0), Module("B", 10, 10, x=10, y=0)],
        bound_width=100,
        bound_height=100,
    )
    overlapping = Floorplan(
        [Module("A", 10, 10, x=0, y=0), Module("B", 10, 10, x=5, y=0)],
        bound_width=100,
        bound_height=100,
    )

    assert calculate_cost(overlapping, config) > calculate_cost(clean, config)
