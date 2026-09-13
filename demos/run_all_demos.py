from __future__ import annotations

import sys
from pathlib import Path

_DEMOS = Path(__file__).resolve().parent
if str(_DEMOS) not in sys.path:
    sys.path.insert(0, str(_DEMOS))

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
