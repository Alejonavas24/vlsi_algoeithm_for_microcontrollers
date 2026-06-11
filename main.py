"""Executable example for VLSI floor-planning with simulated annealing."""

from __future__ import annotations

import json
from pathlib import Path

from vlsi_floorplanning.dataset import create_example_modules
from vlsi_floorplanning.experiments import run_module_order_experiment
from vlsi_floorplanning.models import AnnealingConfig
from vlsi_floorplanning.visualization import generate_experiment_visualizations


def _format_table(rows: list[dict[str, float | int | str]]) -> str:
    headers = [
        "configuration",
        "initialArea",
        "finalArea",
        "improvementPercent",
        "finalCost",
        "finalOverlaps",
    ]
    widths = {
        header: max(len(header), *(len(str(row[header])) for row in rows))
        for header in headers
    }
    header_line = " | ".join(header.ljust(widths[header]) for header in headers)
    separator = "-+-".join("-" * widths[header] for header in headers)
    body = [
        " | ".join(str(row[header]).ljust(widths[header]) for header in headers)
        for row in rows
    ]
    return "\n".join([header_line, separator, *body])


def main() -> None:
    config = AnnealingConfig()
    modules = create_example_modules(rotatable=True)
    experiment = run_module_order_experiment(modules, config)

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    generate_experiment_visualizations(experiment, output_dir)

    results_path = output_dir / "results.json"
    results_path.write_text(
        json.dumps(experiment.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("Resultados del experimento VLSI floor-planning")
    print(_format_table(experiment.table_rows()))
    print()
    print(f"Mejor configuracion: {experiment.best_result.configuration_name}")
    print(f"Resultados JSON: {results_path}")
    print(f"Visualizaciones: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
