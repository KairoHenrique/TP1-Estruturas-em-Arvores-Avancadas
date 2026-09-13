"""Treap: BST nas chaves e heap máximo nas prioridades aleatórias."""

from __future__ import annotations

import random
import sys
from dataclasses import dataclass
from typing import Generic, TypeVar

from common.metrics import Metrics

T = TypeVar("T")


@dataclass
class TreapNode(Generic[T]):
    key: T
    priority: float
    left: TreapNode[T] | None = None
    right: TreapNode[T] | None = None


class Treap(Generic[T]):
    def __init__(
        self,
        metrics: Metrics | None = None,
        rng: random.Random | None = None,
    ) -> None:
        self.metrics = metrics or Metrics()
        self.rng = rng or random.Random()
        self.root: TreapNode[T] | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def insert(self, key: T, priority: float | None = None) -> bool:
        chosen = self.rng.random() if priority is None else priority
        before = self._size
        self.root = self._insert(self.root, key, chosen)
        return self._size > before

    def search(self, key: T) -> bool:
        node = self.root
        while node is not None:
            if self.metrics.compare_eq(node.key, key):
                return True
            if self.metrics.compare_lt(key, node.key):
                node = node.left
            else:
                node = node.right
        return False

    def delete(self, key: T) -> bool:
        if not self.search(key):
            return False
        self.root = self._delete(self.root, key)
        self._size -= 1
        return True

    def node_count(self) -> int:
        count = 0
        stack = [self.root] if self.root is not None else []
        while stack:
            node = stack.pop()
            if node is None:
                continue
            count += 1
            stack.append(node.left)
            stack.append(node.right)
        return count

    def height(self) -> int:
        if self.root is None:
            return -1
        max_height = 0
        stack = [(self.root, 0)]
        while stack:
            node, depth = stack.pop()
            max_height = max(max_height, depth)
            if node.left is not None:
                stack.append((node.left, depth + 1))
            if node.right is not None:
                stack.append((node.right, depth + 1))
        return max_height

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
        lines = ["digraph Treap {", '  node [shape=box, fontname="Helvetica"];']
        if self.root is None:
            lines.append('  empty [label="∅", shape=plaintext];')
        else:
            self._dot_walk(self.root, "n0", lines, [1])
        lines.append("}")
        return "\n".join(lines)

    def _insert(self, node: TreapNode[T] | None, key: T, priority: float) -> TreapNode[T]:
        if node is None:
            self.metrics.nodes_created += 1
            self._size += 1
            return TreapNode(key, priority)
        if self.metrics.compare_eq(node.key, key):
            return node
        if self.metrics.compare_lt(key, node.key):
            node.left = self._insert(node.left, key, priority)
            if node.left is not None and node.left.priority > node.priority:
                node = self._rotate_right(node)
        else:
            node.right = self._insert(node.right, key, priority)
            if node.right is not None and node.right.priority > node.priority:
                node = self._rotate_left(node)
        return node

    def _delete(self, node: TreapNode[T] | None, key: T) -> TreapNode[T] | None:
        if node is None:
            return None
        if self.metrics.compare_lt(key, node.key):
            node.left = self._delete(node.left, key)
            return node
        if self.metrics.compare_lt(node.key, key):
            node.right = self._delete(node.right, key)
            return node
        if node.left is None:
            self.metrics.nodes_deleted += 1
            return node.right
        if node.right is None:
            self.metrics.nodes_deleted += 1
            return node.left
        if node.left.priority > node.right.priority:
            node = self._rotate_right(node)
            node.right = self._delete(node.right, key)
        else:
            node = self._rotate_left(node)
            node.left = self._delete(node.left, key)
        return node

    def _rotate_right(self, node: TreapNode[T]) -> TreapNode[T]:
        left = node.left
        assert left is not None
        node.left = left.right
        left.right = node
        self.metrics.rotations += 1
        return left

    def _rotate_left(self, node: TreapNode[T]) -> TreapNode[T]:
        right = node.right
        assert right is not None
        node.right = right.left
        right.left = node
        self.metrics.rotations += 1
        return right

    def _dot_walk(
        self,
        node: TreapNode[T],
        node_id: str,
        lines: list[str],
        next_id: list[int],
    ) -> None:
        priority = f"{node.priority:.2f}"
        lines.append(f'  {node_id} [label="{node.key}\\n p={priority}"];')
        for child, side in ((node.left, "L"), (node.right, "R")):
            if child is None:
                continue
            child_id = f"n{next_id[0]}"
            next_id[0] += 1
            lines.append(f'  {node_id} -> {child_id} [label="{side}"];')
            self._dot_walk(child, child_id, lines, next_id)
