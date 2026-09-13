from _bootstrap import ensure_imports

ensure_imports()

from pathlib import Path

from patricia.patricia import PatriciaTree
from visualization.render import save_tree_figure


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "output" / "figures" / "patricia"
    tree = PatriciaTree()
    tree.insert("casa")
    tree.insert("caso")
    save_tree_figure(
        tree.to_dot(),
        out / "01_apos_insercoes",
        "Patricia — split do prefixo 'cas'",
    )

    tree.insert("cama")
    tree.insert("carro")
    save_tree_figure(
        tree.to_dot(),
        out / "02_divisao_de_prefixos",
        "Patricia — compactação e novas divisões",
    )

    tree.delete("caso")
    save_tree_figure(
        tree.to_dot(),
        out / "03_apos_remocao",
        "Patricia — após remover 'caso' (recompactação)",
    )
    print(f"Figuras da Patricia em {out}")
    print("prefixo 'ca':", tree.words_with_prefix("ca"))


if __name__ == "__main__":
    main()
