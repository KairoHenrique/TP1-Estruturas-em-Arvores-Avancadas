"""Renderiza DOT em PNG (Graphviz) com fallback em matplotlib."""

from __future__ import annotations

import re
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path


def save_tree_figure(dot_source: str, output_path: Path, title: str = "") -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dot_path = output_path.with_suffix(".dot")
    png_path = output_path.with_suffix(".png")
    dot_path.write_text(dot_source, encoding="utf-8")
    if not _render_with_dot_binary(dot_path, png_path):
        _render_with_matplotlib(dot_source, png_path, title)
    return png_path


def _render_with_dot_binary(dot_path: Path, png_path: Path) -> bool:
    binary = shutil.which("dot")
    if binary is None:
        return False
    try:
        subprocess.run(
            [binary, "-Tpng", str(dot_path), "-o", str(png_path)],
            check=True,
            capture_output=True,
        )
        return png_path.exists()
    except (subprocess.CalledProcessError, OSError):
        return False


def _render_with_matplotlib(dot_source: str, png_path: Path, title: str) -> None:
    from common.mpl_backend import configure

    configure()
    import matplotlib.pyplot as plt

    labels, shapes, children = _parse_dot(dot_source)
    roots = _roots(labels, children)
    positions: dict[str, tuple[float, float]] = {}
    cursor = [0.0]
    for root in roots:
        _layout(root, children, 0, cursor, positions)
        cursor[0] += 1.5

    figure, axes = plt.subplots(figsize=(10, 7))
    for parent, edges in children.items():
        if parent not in positions:
            continue
        x1, y1 = positions[parent]
        for edge_label, child in edges:
            if child not in positions:
                continue
            x2, y2 = positions[child]
            axes.annotate(
                "",
                xy=(x2, y2),
                xytext=(x1, y1),
                arrowprops={"arrowstyle": "->", "color": "#444444", "lw": 1.1},
            )
            axes.text(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                edge_label,
                ha="center",
                va="bottom",
                fontsize=8,
                color="#1f4e79",
            )

    for node_id, (x, y) in positions.items():
        is_double = shapes.get(node_id) == "doublecircle"
        facecolor = "#d6eadf" if is_double else "#f4f4f4"
        circle = plt.Circle((x, y), 0.38, facecolor=facecolor, edgecolor="#222222", lw=1.4)
        axes.add_patch(circle)
        if is_double:
            ring = plt.Circle((x, y), 0.46, fill=False, edgecolor="#222222", lw=1.0)
            axes.add_patch(ring)
        axes.text(x, y, labels.get(node_id, node_id), ha="center", va="center", fontsize=8)

    if not positions:
        axes.text(0.5, 0.5, "árvore vazia", ha="center", va="center")
        axes.set_xlim(0, 1)
        axes.set_ylim(0, 1)
    else:
        xs = [pos[0] for pos in positions.values()]
        ys = [pos[1] for pos in positions.values()]
        axes.set_xlim(min(xs) - 1.2, max(xs) + 1.2)
        axes.set_ylim(min(ys) - 1.2, max(ys) + 1.2)

    axes.set_aspect("equal")
    axes.axis("off")
    if title:
        axes.set_title(title)
    figure.tight_layout()
    figure.savefig(png_path, dpi=160)
    plt.close(figure)


def _parse_dot(
    source: str,
) -> tuple[dict[str, str], dict[str, str], dict[str, list[tuple[str, str]]]]:
    labels: dict[str, str] = {}
    shapes: dict[str, str] = {}
    children: dict[str, list[tuple[str, str]]] = defaultdict(list)
    node_pattern = re.compile(
        r'^\s*([A-Za-z0-9_]+)\s*\[label="([^"]*)"(?:,\s*shape=([A-Za-z]+))?\]',
        re.MULTILINE,
    )
    edge_pattern = re.compile(
        r'^\s*([A-Za-z0-9_]+)\s*->\s*([A-Za-z0-9_]+)(?:\s*\[label="([^"]*)"\])?',
        re.MULTILINE,
    )
    for match in node_pattern.finditer(source):
        node_id, label, shape = match.groups()
        labels[node_id] = label.replace("\\n", "\n")
        if shape:
            shapes[node_id] = shape
    for match in edge_pattern.finditer(source):
        parent, child, edge_label = match.groups()
        children[parent].append((edge_label or "", child))
        labels.setdefault(parent, parent)
        labels.setdefault(child, child)
    return labels, shapes, children


def _roots(labels: dict[str, str], children: dict[str, list[tuple[str, str]]]) -> list[str]:
    pointed = {child for edges in children.values() for _, child in edges}
    roots = [node for node in labels if node not in pointed]
    return roots or list(labels)


def _layout(
    node: str,
    children: dict[str, list[tuple[str, str]]],
    depth: int,
    cursor: list[float],
    positions: dict[str, tuple[float, float]],
) -> float:
    kids = children.get(node, [])
    if not kids:
        x = cursor[0]
        cursor[0] += 1.6
        positions[node] = (x, -depth * 1.6)
        return x
    xs = [_layout(child, children, depth + 1, cursor, positions) for _, child in kids]
    x = sum(xs) / len(xs)
    positions[node] = (x, -depth * 1.6)
    return x
