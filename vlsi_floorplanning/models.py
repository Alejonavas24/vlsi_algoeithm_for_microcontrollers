"""Core data models for rectangular-coordinate floor-planning.

This project intentionally uses direct rectangle coordinates instead of more
specialized VLSI encodings such as B*-Tree or O-Tree. The goal is to keep the
paper's module-order and simulated-annealing ideas easy to inspect and adapt.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import copy


@dataclass
class Module:
    """A rectangular module placed inside a floor-plan bounding rectangle."""

    id: str
    width: float
    height: float
    x: float = 0.0
    y: float = 0.0
    rotatable: bool = False

    @property
    def area(self) -> float:
        return self.width * self.height

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    def rotate(self) -> None:
        if self.rotatable:
            self.width, self.height = self.height, self.width

    def clamp_to_bounds(self, bound_width: float, bound_height: float) -> None:
        max_x = max(0.0, bound_width - self.width)
        max_y = max(0.0, bound_height - self.height)
        self.x = min(max(0.0, self.x), max_x)
        self.y = min(max(0.0, self.y), max_y)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "x": round(self.x, 4),
            "y": round(self.y, 4),
            "width": round(self.width, 4),
            "height": round(self.height, 4),
            "rotatable": self.rotatable,
        }


@dataclass
class Floorplan:
    """A candidate layout and its bounding rectangle."""

    modules: list[Module]
    bound_width: float
    bound_height: float
    name: str = ""

    @property
    def total_module_area(self) -> float:
        return sum(module.area for module in self.modules)

    @property
    def bounding_area(self) -> float:
        return self.bound_width * self.bound_height

    def clone(self) -> "Floorplan":
        return copy.deepcopy(self)

    def clamp_modules(self) -> None:
        for module in self.modules:
            module.clamp_to_bounds(self.bound_width, self.bound_height)

    def module_by_id(self, module_id: str) -> Module:
        for module in self.modules:
            if module.id == module_id:
                return module
        raise KeyError(f"Module {module_id!r} not found")

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "boundWidth": round(self.bound_width, 4),
            "boundHeight": round(self.bound_height, 4),
            "modules": [module.to_dict() for module in self.modules],
        }


@dataclass
class AnnealingConfig:
    initial_temperature: float = 1000.0
    min_temperature: float = 0.01
    iterations: int = 40
    moves_per_temperature: int = 100
    cooling_profile: str = "linear"
    move_step_ratio: float = 0.10
    overlap_penalty_factor: float = 10000.0
    boundary_penalty_factor: float = 10000.0
    dead_space_weight: float = 0.10
    random_seed: int = 42


@dataclass
class AnnealingResult:
    configuration_name: str
    initial_floorplan: Floorplan
    relaxed_floorplan: Floorplan
    final_floorplan: Floorplan
    initial_area: float
    final_area: float
    improvement_percent: float
    final_cost: float
    final_overlaps: int
    history: list[dict[str, float]] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "configuration": self.configuration_name,
            "initialArea": round(self.initial_area, 4),
            "finalArea": round(self.final_area, 4),
            "improvementPercent": round(self.improvement_percent, 4),
            "finalCost": round(self.final_cost, 4),
            "finalOverlaps": self.final_overlaps,
            "metrics": {key: round(value, 4) for key, value in self.metrics.items()},
            "history": self.history,
            "initialFloorplan": self.initial_floorplan.to_dict(),
            "relaxedFloorplan": self.relaxed_floorplan.to_dict(),
            "finalFloorplan": self.final_floorplan.to_dict(),
        }
