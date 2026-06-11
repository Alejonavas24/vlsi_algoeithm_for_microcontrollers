import random

from vlsi_floorplanning.annealing import should_accept
from vlsi_floorplanning.cost import (
    calculate_cost,
    calculate_out_of_bounds_area,
    count_overlaps,
)
from vlsi_floorplanning.dataset import create_example_modules
from vlsi_floorplanning.experiments import (
    generate_initial_orders,
    run_module_order_experiment,
)
from vlsi_floorplanning.models import AnnealingConfig


def test_probabilistic_acceptance_is_seeded() -> None:
    assert should_accept(delta_cost=-1, temperature=1, rng=random.Random(0))
    assert should_accept(delta_cost=1, temperature=1000, rng=random.Random(0))
    assert not should_accept(delta_cost=1000, temperature=1, rng=random.Random(0))


def test_generate_initial_orders_exact_names() -> None:
    orders = generate_initial_orders(create_example_modules())

    assert {name: "".join(module.id for module in modules) for name, modules in orders.items()} == {
        "FP_1": "ABCDEFGHIJ",
        "FP_2": "FJDEGHCIBA",
        "FP_3": "CEBFJHDAGI",
        "FP_4": "ABCDEFGJIH",
        "FP_5": "HBCDEFGAIJ",
        "FP_6": "HGEJBAIDCF",
    }


def test_full_experiment_reduces_area_or_cost_and_stays_in_bounds() -> None:
    config = AnnealingConfig(iterations=5, moves_per_temperature=30, random_seed=42)
    experiment = run_module_order_experiment(create_example_modules(), config)

    assert len(experiment.results) == 6
    for result in experiment.results:
        initial_cost = calculate_cost(result.initial_floorplan, config)
        assert result.final_area <= result.initial_area or result.final_cost <= initial_cost
        assert calculate_out_of_bounds_area(result.final_floorplan) == 0

    assert count_overlaps(experiment.best_result.final_floorplan) == 0
    assert experiment.best_result.final_area <= experiment.best_result.initial_area
