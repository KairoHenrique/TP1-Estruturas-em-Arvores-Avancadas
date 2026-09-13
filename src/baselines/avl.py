"""AVL com fator de balanceamento e rotações simples/duplas."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Generic, TypeVar

from common.metrics import Metrics

T = TypeVar("T")


@dataclass
class AVLNode(Generic[T]):
    key: T
    left: AVLNode[T] | None = None
    right: AVLNode[T] | None = None
    height: int = 0


class AVLTree(Generic[T]):
    def __init__(self, metrics: Metrics | None = None) -> None:
        self.metrics = metrics or Metrics()
        self.root: AVLNode[T] | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def insert(self, key: T) -> bool:
        before = self._size
        self.root = self._insert(self.root, key)
        return self._size > before

    def search(self, key: T) -> bool:
        node = self.root
        while node is not None:
            if self.metrics.compare_eq(key, node.key):
                return True
            node = node.left if self.metrics.compare_lt(key, node.key) else node.right
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
        return self._node_height(self.root)

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
        lines = ["digraph AVL {", '  node [shape=circle, fontname="Helvetica"];']
        if self.root is None:
            lines.append('  empty [label="∅", shape=plaintext];')
        else:
            self._dot_walk(self.root, "n0", lines, [1])
        lines.append("}")
        return "\n".join(lines)

    def _insert(self, node: AVLNode[T] | None, key: T) -> AVLNode[T]:
        if node is None:
            self.metrics.nodes_created += 1
            self._size += 1
            return AVLNode(key)
        if self.metrics.compare_eq(key, node.key):
            return node
        if self.metrics.compare_lt(key, node.key):
            node.left = self._insert(node.left, key)
        else:
            node.right = self._insert(node.right, key)
        return self._rebalance(node)

    def _delete(self, node: AVLNode[T] | None, key: T) -> AVLNode[T] | None:
        if node is None:
            return None
        if self.metrics.compare_lt(key, node.key):
            node.left = self._delete(node.left, key)
        elif self.metrics.compare_lt(node.key, key):
            node.right = self._delete(node.right, key)
        else:
            if node.left is None:
                self.metrics.nodes_deleted += 1
                return node.right
            if node.right is None:
                self.metrics.nodes_deleted += 1
                return node.left
            successor = self._min_node(node.right)
            node.key = successor.key
            node.right = self._delete(node.right, successor.key)
        return self._rebalance(node)

    def _rebalance(self, node: AVLNode[T]) -> AVLNode[T]:
        self._update_height(node)
        balance = self._balance_factor(node)
        if balance > 1:
            if self._balance_factor(node.left) < 0:
                node.left = self._rotate_left(node.left)  # type: ignore[arg-type]
            return self._rotate_right(node)
        if balance < -1:
            if self._balance_factor(node.right) > 0:
                node.right = self._rotate_right(node.right)  # type: ignore[arg-type]
            return self._rotate_left(node)
        return node

    def _rotate_right(self, node: AVLNode[T]) -> AVLNode[T]:
        left = node.left
        assert left is not None
        node.left = left.right
        left.right = node
        self._update_height(node)
        self._update_height(left)
        self.metrics.rotations += 1
        return left

    def _rotate_left(self, node: AVLNode[T]) -> AVLNode[T]:
        right = node.right
        assert right is not None
        node.right = right.left
        right.left = node
        self._update_height(node)
        self._update_height(right)
        self.metrics.rotations += 1
        return right

    def _node_height(self, node: AVLNode[T] | None) -> int:
        return -1 if node is None else node.height

    def _update_height(self, node: AVLNode[T]) -> None:
        node.height = 1 + max(self._node_height(node.left), self._node_height(node.right))

    def _balance_factor(self, node: AVLNode[T] | None) -> int:
        if node is None:
            return 0
        return self._node_height(node.left) - self._node_height(node.right)

    def _min_node(self, node: AVLNode[T]) -> AVLNode[T]:
        while node.left is not None:
            node = node.left
        return node

    def _dot_walk(
        self,
        node: AVLNode[T],
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
