from _bootstrap import ensure_imports

ensure_imports()

from pathlib import Path

from trie.trie import Trie
from visualization.render import save_tree_figure


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "output" / "figures" / "trie"
    tree = Trie()
    tree.insert("casa")
    tree.insert("caso")
    tree.insert("cama")
    tree.insert("carro")
    save_tree_figure(tree.to_dot(), out / "01_apos_insercoes", "Trie — após inserções")

    tree.insert("cardapio")
    tree.insert("carta")
    save_tree_figure(
        tree.to_dot(),
        out / "02_bifurcacao_prefixo",
        "Trie — compartilhamento de prefixo (car)",
    )

    tree.delete("carro")
    save_tree_figure(tree.to_dot(), out / "03_apos_remocao", "Trie — após remover 'carro'")
    print(f"Figuras da Trie em {out}")
    print("prefixo 'cas':", tree.words_with_prefix("cas"))


if __name__ == "__main__":
    main()
