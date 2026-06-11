# VLSI Floor-Planning con Simulated Annealing

Implementacion pragmatica de floor-planning VLSI basada en el enfoque del paper
"Effect of Module Order on VLSI Floor Planning using Simulated Annealing".

El proyecto usa coordenadas rectangulares directas `(x, y, width, height)`, no
representaciones avanzadas como B*-Tree u O-Tree. El foco es comparar distintos
ordenes iniciales de modulos, relajar overlaps, aplicar simulated annealing y
escoger el layout final con menor area valida.

## Instalacion

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

## Ejecucion

```bash
python main.py
```

El programa ejecuta las seis configuraciones `FP_1` a `FP_6`, imprime una tabla
con resultados y genera artefactos en `outputs/`:

- `results.json`: salida estructurada con mejor configuracion, metricas,
  modulos finales e historial.
- `FP_*_initial.svg`: floor-plan inicial de cada configuracion.
- `FP_*_relaxed.svg`: floor-plan despues de relajacion.
- `FP_*_final.svg`: floor-plan final.
- `area_history.svg`: curva comparativa de area por iteracion.

## Cambiar modulos

El dataset de ejemplo esta en `vlsi_floorplanning/dataset.py`:

```python
Module("A", 40, 50, rotatable=True)
```

Puedes agregar, quitar o cambiar dimensiones. El bounding rectangle se calcula
automaticamente como un area aproximada de `1.5 * sum(width * height)`.

## Cambiar annealing

Los parametros estan en `AnnealingConfig`:

```python
AnnealingConfig(
    initial_temperature=1000.0,
    min_temperature=0.01,
    iterations=40,
    moves_per_temperature=100,
    cooling_profile="linear",
    move_step_ratio=0.10,
    overlap_penalty_factor=10000.0,
    boundary_penalty_factor=10000.0,
    dead_space_weight=0.10,
    random_seed=42,
)
```

`cooling_profile` acepta:

- `linear`
- `logarithmic`

## Interpretacion

La tabla reporta:

- `initialArea`: area usada antes de relajar/optimizar.
- `finalArea`: area usada por la mejor solucion final de esa configuracion.
- `improvementPercent`: reduccion porcentual frente al area inicial.
- `finalCost`: costo total con penalizaciones.
- `finalOverlaps`: numero de pares de modulos solapados.

La mejor configuracion se elige por menor area final valida sin overlaps ni
salidas del bounding rectangle. Si ninguna configuracion queda perfecta, se usa
el menor costo con menor overlap.

## Pruebas

```bash
pytest
```
