from _bootstrap import ensure_imports

ensure_imports()

from pathlib import Path

from kdtree.kdtree import KDTree
from visualization.kd_plot import plot_kd_tree
from visualization.render import save_tree_figure


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "output" / "figures" / "kdtree"
    tree = KDTree(dimensions=2)
    points = [
        (5.0, 5.0),
        (2.0, 7.0),
        (8.0, 3.0),
        (3.0, 2.0),
        (7.0, 8.0),
        (9.0, 6.0),
    ]
    for point in points[:4]:
        tree.insert(point)
    bounds = (0.0, 10.0, 0.0, 10.0)
    save_tree_figure(tree.to_dot(), out / "01_apos_insercoes_arvore", "KD-Tree — após 4 inserções")
    plot_kd_tree(tree, out / "01_apos_insercoes_plano", "KD-Tree — partição espacial inicial", bounds=bounds)

    for point in points[4:]:
        tree.insert(point)
    save_tree_figure(
        tree.to_dot(),
        out / "02_particionamento_arvore",
        "KD-Tree — após novas inserções",
    )
    plot_kd_tree(
        tree,
        out / "02_particionamento_plano",
        "KD-Tree — partições após 6 pontos",
        bounds=bounds,
    )

    tree.delete((8.0, 3.0))
    query = (6.5, 7.5)
    nearest = tree.nearest(query)
    save_tree_figure(tree.to_dot(), out / "03_apos_remocao_arvore", "KD-Tree — após remover (8,3)")
    plot_kd_tree(
        tree,
        out / "03_apos_remocao_nn",
        "KD-Tree — remoção e vizinho mais próximo",
        query=query,
        nearest=nearest,
        bounds=bounds,
    )
    print(f"Figuras da KD-Tree em {out}")
    print("NN de", query, "=", nearest)
    print("range [2,2]–[6,6]:", tree.range_search((2.0, 2.0), (6.0, 6.0)))


if __name__ == "__main__":
    main()
