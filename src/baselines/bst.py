"""BST clássica sem balanceamento, usada como baseline experimental."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Generic, TypeVar

from common.metrics import Metrics

T = TypeVar("T")


@dataclass
class BSTNode(Generic[T]):
    key: T
    left: BSTNode[T] | None = None
    right: BSTNode[T] | None = None


class BinarySearchTree(Generic[T]):
    def __init__(self, metrics: Metrics | None = None) -> None:
        self.metrics = metrics or Metrics()
        self.root: BSTNode[T] | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def insert(self, key: T) -> bool:
        if self.root is None:
            self.root = BSTNode(key)
            self.metrics.nodes_created += 1
            self._size += 1
            return True
        parent = None
        node = self.root
        went_left = False
        while node is not None:
            parent = node
            if self.metrics.compare_eq(key, node.key):
                return False
            went_left = self.metrics.compare_lt(key, node.key)
            node = node.left if went_left else node.right
        new_node = BSTNode(key)
        self.metrics.nodes_created += 1
        if went_left:
            parent.left = new_node  # type: ignore[union-attr]
        else:
            parent.right = new_node  # type: ignore[union-attr]
        self._size += 1
        return True

    def search(self, key: T) -> bool:
        node = self.root
        while node is not None:
            if self.metrics.compare_eq(key, node.key):
                return True
            node = node.left if self.metrics.compare_lt(key, node.key) else node.right
        return False

    def delete(self, key: T) -> bool:
        self.root, removed = self._delete(self.root, key)
        if removed:
            self._size -= 1
        return removed

    def node_count(self) -> int:
        return _iterative_count(self.root)

    def height(self) -> int:
        return _iterative_height(self.root)

    def estimate_memory_bytes(self) -> int:
        total = 0
        stack = [self.root] if self.root else []
        while stack:
            node = stack.pop()
            if node is None:
                continue
            total += sys.getsizeof(node)
            stack.append(node.left)
            stack.append(node.right)
        return total

    def to_dot(self) -> str:
        lines = ["digraph BST {", '  node [shape=circle, fontname="Helvetica"];']
        if self.root is None:
            lines.append('  empty [label="∅", shape=plaintext];')
        else:
            self._dot_walk(self.root, "n0", lines, [1])
        lines.append("}")
        return "\n".join(lines)

    def _delete(self, node: BSTNode[T] | None, key: T) -> tuple[BSTNode[T] | None, bool]:
        if node is None:
            return None, False
        if self.metrics.compare_lt(key, node.key):
            node.left, removed = self._delete(node.left, key)
            return node, removed
        if self.metrics.compare_lt(node.key, key):
            node.right, removed = self._delete(node.right, key)
            return node, removed
        if node.left is None:
            self.metrics.nodes_deleted += 1
            return node.right, True
        if node.right is None:
            self.metrics.nodes_deleted += 1
            return node.left, True
        successor = node.right
        while successor.left is not None:
            successor = successor.left
        node.key = successor.key
        node.right, _ = self._delete(node.right, successor.key)
        return node, True

    def _dot_walk(
        self,
        node: BSTNode[T],
        node_id: str,
        lines: list[str],
        next_id: list[int],
    ) -> None:
        lines.append(f'  {node_id} [label="{node.key}"];')
        for child, side in ((node.left, "L"), (node.right, "R")):
            if child is None:
                continue
            child_id = f"n{next_id[0]}"
            next_id[0] += 1
            lines.append(f'  {node_id} -> {child_id} [label="{side}"];')
            self._dot_walk(child, child_id, lines, next_id)


def _iterative_count(root: BSTNode | None) -> int:
    count = 0
    stack = [root] if root is not None else []
    while stack:
        node = stack.pop()
        if node is None:
            continue
        count += 1
        stack.append(node.left)
        stack.append(node.right)
    return count


def _iterative_height(root: BSTNode | None) -> int:
    if root is None:
        return -1
    max_height = 0
    stack = [(root, 0)]
    while stack:
        node, depth = stack.pop()
        max_height = max(max_height, depth)
        if node.left is not None:
            stack.append((node.left, depth + 1))
        if node.right is not None:
            stack.append((node.right, depth + 1))
    return max_height
