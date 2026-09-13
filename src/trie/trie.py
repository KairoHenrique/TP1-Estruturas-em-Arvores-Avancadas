"""Trie (árvore de prefixos) com um caractere por aresta."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field

from common.metrics import Metrics


@dataclass
class TrieNode:
    children: dict[str, "TrieNode"] = field(default_factory=dict)
    is_end: bool = False


class Trie:
    def __init__(self, metrics: Metrics | None = None) -> None:
        self.metrics = metrics or Metrics()
        self.root = TrieNode()
        self.metrics.nodes_created += 1
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def insert(self, word: str) -> bool:
        if not isinstance(word, str):
            raise TypeError("Trie só aceita chaves string.")
        node = self.root
        for char in word:
            child = node.children.get(char)
            if child is None:
                child = TrieNode()
                node.children[char] = child
                self.metrics.nodes_created += 1
            node = child
            self.metrics.comparisons += 1
        if node.is_end:
            return False
        node.is_end = True
        self._size += 1
        return True

    def search(self, word: str) -> bool:
        node = self._walk(word)
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> bool:
        return self._walk(prefix) is not None

    def words_with_prefix(self, prefix: str) -> list[str]:
        node = self._walk(prefix)
        if node is None:
            return []
        collected: list[str] = []
        self._collect(node, prefix, collected)
        return collected

    def delete(self, word: str) -> bool:
        if self._delete_from(self.root, word, 0):
            self._size -= 1
            return True
        return False

    def node_count(self) -> int:
        return self._count_nodes(self.root)

    def estimate_memory_bytes(self) -> int:
        total = 0
        stack = [self.root]
        while stack:
            node = stack.pop()
            total += sys.getsizeof(node) + sys.getsizeof(node.children)
            stack.extend(node.children.values())
        return total

    def to_dot(self) -> str:
        lines = [
            "digraph Trie {",
            "  rankdir=TB;",
            '  node [fontname="Helvetica"];',
        ]
        self._dot_walk(self.root, "n0", lines, [1])
        lines.append("}")
        return "\n".join(lines)

    def _walk(self, text: str) -> TrieNode | None:
        node = self.root
        for char in text:
            self.metrics.comparisons += 1
            node = node.children.get(char)
            if node is None:
                return None
        return node

    def _delete_from(self, node: TrieNode, word: str, index: int) -> bool:
        if index == len(word):
            if not node.is_end:
                return False
            node.is_end = False
            return True

        char = word[index]
        child = node.children.get(char)
        self.metrics.comparisons += 1
        if child is None:
            return False
        removed = self._delete_from(child, word, index + 1)
        if removed and not child.is_end and not child.children:
            del node.children[char]
            self.metrics.nodes_deleted += 1
        return removed

    def _collect(self, node: TrieNode, prefix: str, collected: list[str]) -> None:
        if node.is_end:
            collected.append(prefix)
        for char, child in sorted(node.children.items()):
            self._collect(child, prefix + char, collected)

    def _count_nodes(self, node: TrieNode) -> int:
        return 1 + sum(self._count_nodes(child) for child in node.children.values())

    def _dot_walk(
        self,
        node: TrieNode,
        node_id: str,
        lines: list[str],
        next_id: list[int],
    ) -> None:
        shape = "doublecircle" if node.is_end else "circle"
        label = "ε" if node_id == "n0" else ""
        lines.append(f'  {node_id} [label="{label}", shape={shape}];')
        for char, child in sorted(node.children.items()):
            child_id = f"n{next_id[0]}"
            next_id[0] += 1
            lines.append(f'  {node_id} -> {child_id} [label="{char}"];')
            self._dot_walk(child, child_id, lines, next_id)
