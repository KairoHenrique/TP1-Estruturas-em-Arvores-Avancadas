from _bootstrap import ensure_imports

ensure_imports()

from pathlib import Path

from splay.splay import SplayTree
from visualization.render import save_tree_figure


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "output" / "figures" / "splay"
    tree = SplayTree()
    for key in (10, 20, 30, 40, 50):
        tree.insert(key)
    save_tree_figure(
        tree.to_dot(),
        out / "01_apos_insercoes",
        "Splay — após inserções (último inserido na raiz)",
    )

    tree.search(10)
    save_tree_figure(
        tree.to_dot(),
        out / "02_apos_splay_do_10",
        "Splay — busca de 10 (zig-zig até a raiz)",
    )

    tree.delete(30)
    save_tree_figure(tree.to_dot(), out / "03_apos_remocao", "Splay — após remover 30")
    print(f"Figuras da Splay em {out}")
    print("raiz:", None if tree.root is None else tree.root.key)


if __name__ == "__main__":
    main()
