"""Gráficos matplotlib a partir do CSV experimental."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any


def plot_results(csv_path: Path, output_dir: Path) -> None:
    from common.mpl_backend import configure

    configure()
    import matplotlib.pyplot as plt

    rows = _read_csv(csv_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    _plot_strings(rows, output_dir, plt)
    _plot_ordered(rows, output_dir, plt)
    _plot_kdtree(rows, output_dir, plt)


def _read_csv(csv_path: Path) -> list[dict[str, Any]]:
    with csv_path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _plot_strings(rows: list[dict[str, Any]], output_dir: Path, plt: Any) -> None:
    subset = [row for row in rows if row["group"] == "strings"]
    figure, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    _line_by_structure(axes[0], subset, "insert", "seconds", "Inserção (strings)")
    _line_by_structure(axes[1], subset, "search", "seconds", "Busca (strings)")
    figure.tight_layout()
    figure.savefig(output_dir / "strings_tempo.png", dpi=160)
    plt.close(figure)

    figure, axes = plt.subplots(figsize=(7, 4.8))
    _line_by_structure(axes, subset, "insert", "nodes", "Nós após inserção (strings)")
    figure.tight_layout()
    figure.savefig(output_dir / "strings_nos.png", dpi=160)
    plt.close(figure)


def _plot_ordered(rows: list[dict[str, Any]], output_dir: Path, plt: Any) -> None:
    subset = [row for row in rows if row["group"] == "ordenaveis"]
    for pattern in ("aleatorio", "ordenado", "zipf", "localidade"):
        data = [row for row in subset if row["pattern"] == pattern]
        if not data:
            continue
        operation = "insert" if pattern in {"aleatorio", "ordenado"} else "search"
        usable = [row for row in data if row["operation"] == operation]
        if not usable:
            usable = [row for row in data if row["operation"] == "search"]
        figure, axes = plt.subplots(figsize=(7.5, 4.8))
        _line_by_structure(axes, usable, usable[0]["operation"], "seconds", f"Tempo — {pattern}")
        figure.tight_layout()
        figure.savefig(output_dir / f"ordenaveis_{pattern}.png", dpi=160)
        plt.close(figure)


def _plot_kdtree(rows: list[dict[str, Any]], output_dir: Path, plt: Any) -> None:
    subset = [row for row in rows if row["group"] == "espacial" and row["operation"] == "nearest"]
    figure, axes = plt.subplots(figsize=(7.5, 4.8))
    _line_by_structure(
        axes,
        [row for row in subset if row["pattern"] == "2d"],
        "nearest",
        "seconds",
        "NN 2D: KD-Tree vs força bruta",
    )
    figure.tight_layout()
    figure.savefig(output_dir / "kdtree_nn_2d.png", dpi=160)
    plt.close(figure)


def _line_by_structure(
    axes: Any,
    rows: list[dict[str, Any]],
    operation: str,
    field: str,
    title: str,
) -> None:
    grouped: dict[str, list[tuple[int, float]]] = defaultdict(list)
    for row in rows:
        if row["operation"] != operation:
            continue
        grouped[row["structure"]].append((int(row["n"]), float(row[field])))
    for name, series in sorted(grouped.items()):
        series.sort()
        xs = [item[0] for item in series]
        ys = [item[1] for item in series]
        axes.plot(xs, ys, marker="o", label=name)
    axes.set_xlabel("n")
    axes.set_ylabel(field)
    axes.set_title(title)
    axes.grid(True, alpha=0.3)
    axes.legend()
