from demo_kdtree import main as demo_kdtree
from demo_patricia import main as demo_patricia
from demo_splay import main as demo_splay
from demo_treap import main as demo_treap
from demo_trie import main as demo_trie


def main() -> None:
    demo_trie()
    demo_patricia()
    demo_splay()
    demo_treap()
    demo_kdtree()


if __name__ == "__main__":
    main()
