"""Verificação rápida de corretude das cinco estruturas e das baselines."""

from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from baselines.avl import AVLTree
from baselines.bst import BinarySearchTree
from kdtree.kdtree import KDTree
from patricia.patricia import PatriciaTree
from splay.splay import SplayTree
from treap.treap import Treap
from trie.trie import Trie


def main() -> None:
    test_trie()
    test_patricia()
    test_splay()
    test_treap()
    test_kdtree()
    test_bst_avl()
    print("Sanity: todas as estruturas passaram.")


def test_trie() -> None:
    tree = Trie()
    for word in ("casa", "caso", "cama", "carro"):
        assert tree.insert(word)
    assert not tree.insert("casa")
    assert tree.search("casa")
    assert not tree.search("cas")
    assert tree.starts_with("cas")
    assert set(tree.words_with_prefix("cas")) == {"casa", "caso"}
    assert tree.delete("carro")
    assert not tree.search("carro")
    assert tree.search("carta") is False
    assert len(tree) == 3


def test_patricia() -> None:
    tree = PatriciaTree()
    for word in ("casa", "caso", "cama", "carro"):
        assert tree.insert(word)
    assert not tree.insert("caso")
    assert tree.search("casa")
    assert not tree.search("cas")
    assert tree.starts_with("cas")
    assert set(tree.words_with_prefix("cas")) == {"casa", "caso"}
    assert tree.delete("caso")
    assert not tree.search("caso")
    assert tree.search("casa")
    assert tree.starts_with("ca")
    remaining = set(tree.words_with_prefix(""))
    assert remaining == {"casa", "cama", "carro"}


def test_splay() -> None:
    tree = SplayTree()
    for key in range(1, 11):
        assert tree.insert(key)
    assert tree.search(1)
    assert tree.root is not None and tree.root.key == 1
    assert tree.delete(7)
    assert not tree.search(7)
    assert not tree.insert(3)
    assert len(tree) == 9


def test_treap() -> None:
    tree = Treap(rng=random.Random(13))
    for key in (5, 2, 8, 1, 4, 7, 9):
        assert tree.insert(key)
    assert tree.search(4)
    assert not tree.search(6)
    assert tree.delete(8)
    assert not tree.search(8)
    assert _is_bst(tree.root) and _is_heap(tree.root)
    assert len(tree) == 6


def test_kdtree() -> None:
    tree = KDTree(2)
    points = [(2.0, 3.0), (5.0, 4.0), (9.0, 6.0), (4.0, 7.0), (8.0, 1.0)]
    for point in points:
        assert tree.insert(point)
    assert tree.search((5.0, 4.0))
    nearest = tree.nearest((9.0, 2.0))
    assert nearest == (8.0, 1.0)
    found = set(tree.range_search((1.0, 2.0), (5.0, 5.0)))
    assert (2.0, 3.0) in found and (5.0, 4.0) in found
    assert tree.delete((5.0, 4.0))
    assert not tree.search((5.0, 4.0))
    assert tree.nearest((5.0, 4.0)) != (5.0, 4.0)


def test_bst_avl() -> None:
    for factory in (BinarySearchTree, AVLTree):
        tree = factory()
        for key in (10, 5, 15, 3, 7, 12, 18):
            assert tree.insert(key)
        assert tree.search(7)
        assert tree.delete(10)
        assert not tree.search(10)
        assert tree.search(12)
        assert _is_bst(tree.root)


def _is_bst(node, low=None, high=None) -> bool:
    if node is None:
        return True
    if low is not None and node.key <= low:
        return False
    if high is not None and node.key >= high:
        return False
    return _is_bst(node.left, low, node.key) and _is_bst(node.right, node.key, high)


def _is_heap(node) -> bool:
    if node is None:
        return True
    for child in (node.left, node.right):
        if child is not None and child.priority > node.priority:
            return False
    return _is_heap(node.left) and _is_heap(node.right)


if __name__ == "__main__":
    main()
