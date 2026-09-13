"""Árvore Splay com splay bottom-up recursivo (zig, zig-zig, zig-zag)."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Generic, TypeVar

from common.metrics import Metrics

T = TypeVar("T")


@dataclass
class SplayNode(Generic[T]):
    key: T
    left: SplayNode[T] | None = None
    right: SplayNode[T] | None = None


class SplayTree(Generic[T]):
    def __init__(self, metrics: Metrics | None = None) -> None:
        self.metrics = metrics or Metrics()
        self.root: SplayNode[T] | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def insert(self, key: T) -> bool:
        if self.root is None:
            self.root = SplayNode(key)
            self.metrics.nodes_created += 1
            self._size += 1
            return True
        self.root = self._splay(self.root, key)
        if self.metrics.compare_eq(self.root.key, key):
            return False
        new_node = SplayNode(key)
        self.metrics.nodes_created += 1
        if self.metrics.compare_lt(key, self.root.key):
            new_node.left = self.root.left
            new_node.right = self.root
            self.root.left = None
        else:
            new_node.right = self.root.right
            new_node.left = self.root
            self.root.right = None
        self.root = new_node
        self._size += 1
        return True

    def search(self, key: T) -> bool:
        if self.root is None:
            return False
        self.root = self._splay(self.root, key)
        return self.metrics.compare_eq(self.root.key, key)

    def delete(self, key: T) -> bool:
        if self.root is None:
            return False
        self.root = self._splay(self.root, key)
        if not self.metrics.compare_eq(self.root.key, key):
            return False
        if self.root.left is None:
            self.root = self.root.right
        else:
            right = self.root.right
            self.root = self._splay(self.root.left, key)
            self.root.right = right
        self.metrics.nodes_deleted += 1
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
        lines = ["digraph Splay {", '  node [shape=circle, fontname="Helvetica"];']
        if self.root is None:
            lines.append('  empty [label="∅", shape=plaintext];')
        else:
            self._dot_walk(self.root, "n0", lines, [1])
        lines.append("}")
        return "\n".join(lines)

    def _rotate_right(self, node: SplayNode[T]) -> SplayNode[T]:
        left = node.left
        assert left is not None
        node.left = left.right
        left.right = node
        self.metrics.rotations += 1
        return left

    def _rotate_left(self, node: SplayNode[T]) -> SplayNode[T]:
        right = node.right
        assert right is not None
        node.right = right.left
        right.left = node
        self.metrics.rotations += 1
        return right

    def _splay(self, node: SplayNode[T] | None, key: T) -> SplayNode[T] | None:
        if node is None or self.metrics.compare_eq(node.key, key):
            return node
        if self.metrics.compare_lt(key, node.key):
            if node.left is None:
                return node
            if self.metrics.compare_lt(key, node.left.key):
                node.left.left = self._splay(node.left.left, key)
                node = self._rotate_right(node)
            elif self.metrics.compare_lt(node.left.key, key):
                node.left.right = self._splay(node.left.right, key)
                if node.left.right is not None:
                    node.left = self._rotate_left(node.left)
            return node if node.left is None else self._rotate_right(node)
        if node.right is None:
            return node
        if self.metrics.compare_lt(node.right.key, key):
            node.right.right = self._splay(node.right.right, key)
            node = self._rotate_left(node)
        elif self.metrics.compare_lt(key, node.right.key):
            node.right.left = self._splay(node.right.left, key)
            if node.right.left is not None:
                node.right = self._rotate_right(node.right)
        return node if node.right is None else self._rotate_left(node)

    def _dot_walk(
        self,
        node: SplayNode[T],
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
