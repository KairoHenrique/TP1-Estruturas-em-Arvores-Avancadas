"""Plot 2D da KD-Tree: pontos e retas de partição."""

from __future__ import annotations

from pathlib import Path

from kdtree.kdtree import KDTree, Point


def plot_kd_tree(
    tree: KDTree,
    output_path: Path,
    title: str,
    query: Point | None = None,
    nearest: Point | None = None,
    bounds: tuple[float, float, float, float] = (0.0, 10.0, 0.0, 10.0),
) -> Path:
    import matplotlib.pyplot as plt

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    xmin, xmax, ymin, ymax = bounds
    figure, axes = plt.subplots(figsize=(7, 7))
    axes.set_xlim(xmin, xmax)
    axes.set_ylim(ymin, ymax)
    axes.set_aspect("equal")
    axes.set_xlabel("x")
    axes.set_ylabel("y")
    axes.set_title(title)

    for (x1, y1), (x2, y2) in tree.partition_segments(bounds):
        axes.plot([x1, x2], [y1, y2], color="#888888", lw=1.0, zorder=1)

    points = tree.points()
    if points:
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        axes.scatter(xs, ys, c="#1f4e79", s=40, zorder=3, label="pontos")
        for point in points:
            axes.annotate(f"({point[0]:g},{point[1]:g})", (point[0], point[1]), fontsize=8)

    if query is not None:
        axes.scatter([query[0]], [query[1]], c="#c0392b", marker="x", s=80, zorder=4, label="consulta")
    if nearest is not None:
        axes.scatter(
            [nearest[0]],
            [nearest[1]],
            facecolors="none",
            edgecolors="#27ae60",
            s=140,
            zorder=4,
            label="mais próximo",
        )
        if query is not None:
            axes.plot(
                [query[0], nearest[0]],
                [query[1], nearest[1]],
                color="#27ae60",
                ls="--",
                lw=1.2,
            )

    axes.legend(loc="upper right", fontsize=8)
    figure.tight_layout()
    png_path = output_path.with_suffix(".png")
    figure.savefig(png_path, dpi=160)
    plt.close(figure)
    return png_path
