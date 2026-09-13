from _bootstrap import ensure_imports

ensure_imports()

from pathlib import Path
import random

from treap.treap import Treap
from visualization.render import save_tree_figure


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "output" / "figures" / "treap"
    tree = Treap(rng=random.Random(7))
    tree.insert(20, priority=0.30)
    tree.insert(10, priority=0.20)
    tree.insert(30, priority=0.25)
    tree.insert(40, priority=0.10)
    save_tree_figure(
        tree.to_dot(),
        out / "01_apos_insercoes",
        "Treap — BST nas chaves, heap nas prioridades",
    )

    tree.insert(25, priority=0.90)
    save_tree_figure(
        tree.to_dot(),
        out / "02_prioridade_alta_sobe",
        "Treap — 25 com prioridade 0.90 sobe à raiz",
    )

    tree.delete(25)
    save_tree_figure(
        tree.to_dot(),
        out / "03_apos_remocao",
        "Treap — após remover 25 (rotações para baixo)",
    )
    print(f"Figuras da Treap em {out}")
    print("raiz:", None if tree.root is None else (tree.root.key, round(tree.root.priority, 2)))


if __name__ == "__main__":
    main()
