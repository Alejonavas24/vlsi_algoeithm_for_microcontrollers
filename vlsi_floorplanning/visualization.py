"""SVG/PNG visualizations for floor-planning results."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from .experiments import ExperimentResult
from .models import Floorplan


def draw_floorplan(floorplan: Floorplan, output_path: str | Path, title: str) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.add_patch(
        Rectangle(
            (0, 0),
            floorplan.bound_width,
            floorplan.bound_height,
            fill=False,
            edgecolor="black",
            linewidth=2,
        )
    )
    colors = plt.cm.tab20.colors
    for index, module in enumerate(floorplan.modules):
        color = colors[index % len(colors)]
        ax.add_patch(
            Rectangle(
                (module.x, module.y),
                module.width,
                module.height,
                facecolor=color,
                edgecolor="black",
                linewidth=1.2,
                alpha=0.75,
            )
        )
        ax.text(
            module.x + module.width / 2.0,
            module.y + module.height / 2.0,
            module.id,
            ha="center",
            va="center",
            fontsize=10,
            weight="bold",
            color="black",
        )

    ax.set_title(title)
    ax.set_xlim(-5, floorplan.bound_width + 5)
    ax.set_ylim(floorplan.bound_height + 5, -5)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, linestyle="--", linewidth=0.4, alpha=0.4)
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)


def plot_area_history(experiment: ExperimentResult, output_path: str | Path) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 5))
    for result in experiment.results:
        x_values = [point["iteration"] for point in result.history]
        y_values = [point["bestArea"] for point in result.history]
        ax.plot(x_values, y_values, label=result.configuration_name, linewidth=1.8)

    ax.set_title("Area por iteracion")
    ax.set_xlabel("Iteracion")
    ax.set_ylabel("Mejor area usada")
    ax.grid(True, linestyle="--", linewidth=0.4, alpha=0.4)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)


def generate_experiment_visualizations(
    experiment: ExperimentResult, output_dir: str | Path = "outputs"
) -> None:
    output = Path(output_dir)
    for result in experiment.results:
        draw_floorplan(
            result.initial_floorplan,
            output / f"{result.configuration_name}_initial.svg",
            f"{result.configuration_name} inicial",
        )
        draw_floorplan(
            result.relaxed_floorplan,
            output / f"{result.configuration_name}_relaxed.svg",
            f"{result.configuration_name} relajado",
        )
        draw_floorplan(
            result.final_floorplan,
            output / f"{result.configuration_name}_final.svg",
            f"{result.configuration_name} final",
        )
    plot_area_history(experiment, output / "area_history.svg")
