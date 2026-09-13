"""Árvore Patricia (radix tree compacta) com strings nas arestas."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field

from common.metrics import Metrics


@dataclass
class PatriciaNode:
    children: dict[str, "PatriciaNode"] = field(default_factory=dict)
    is_end: bool = False
    edge: str = ""


class PatriciaTree:
    def __init__(self, metrics: Metrics | None = None) -> None:
        self.metrics = metrics or Metrics()
        self.root = PatriciaNode()
        self.metrics.nodes_created += 1
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def insert(self, word: str) -> bool:
        if not isinstance(word, str):
            raise TypeError("Patricia só aceita chaves string.")
        if word == "":
            if self.root.is_end:
                return False
            self.root.is_end = True
            self._size += 1
            return True
        inserted = self._insert_at(self.root, word)
        if inserted:
            self._size += 1
        return inserted

    def search(self, word: str) -> bool:
        located = self._locate(word)
        if located is None:
            return False
        node, consumed, at_node, _path = located
        return at_node and consumed == len(word) and node.is_end

    def starts_with(self, prefix: str) -> bool:
        if prefix == "":
            return True
        located = self._locate(prefix)
        return located is not None and located[1] == len(prefix)

    def words_with_prefix(self, prefix: str) -> list[str]:
        collected: list[str] = []
        if prefix == "":
            self._collect(self.root, "", collected)
            return collected
        located = self._locate(prefix)
        if located is None or located[1] != len(prefix):
            return []
        node, _consumed, _at_node, path = located
        self._collect(node, path, collected)
        return collected

    def delete(self, word: str) -> bool:
        if not self.search(word):
            return False
        self._delete_at(self.root, word)
        self._compress(self.root)
        self._size -= 1
        return True

    def node_count(self) -> int:
        return self._count_nodes(self.root)

    def estimate_memory_bytes(self) -> int:
        total = 0
        stack = [self.root]
        while stack:
            node = stack.pop()
            total += sys.getsizeof(node) + sys.getsizeof(node.children) + sys.getsizeof(node.edge)
            stack.extend(node.children.values())
        return total

    def to_dot(self) -> str:
        lines = [
            "digraph Patricia {",
            "  rankdir=TB;",
            '  node [fontname="Helvetica"];',
        ]
        self._dot_walk(self.root, "n0", lines, [1])
        lines.append("}")
        return "\n".join(lines)

    def _common_prefix_length(self, left: str, right: str) -> int:
        limit = min(len(left), len(right))
        index = 0
        while index < limit:
            self.metrics.comparisons += 1
            if left[index] != right[index]:
                break
            index += 1
        return index

    def _insert_at(self, node: PatriciaNode, remaining: str) -> bool:
        if remaining == "":
            if node.is_end:
                return False
            node.is_end = True
            return True

        first = remaining[0]
        child = node.children.get(first)
        if child is None:
            new_node = PatriciaNode(edge=remaining, is_end=True)
            node.children[first] = new_node
            self.metrics.nodes_created += 1
            return True

        shared = self._common_prefix_length(child.edge, remaining)
        if shared == len(child.edge):
            return self._insert_at(child, remaining[shared:])

        split = PatriciaNode(edge=child.edge[:shared])
        self.metrics.nodes_created += 1
        child.edge = child.edge[shared:]
        split.children[child.edge[0]] = child
        leftover = remaining[shared:]
        if leftover == "":
            split.is_end = True
        else:
            leaf = PatriciaNode(edge=leftover, is_end=True)
            split.children[leftover[0]] = leaf
            self.metrics.nodes_created += 1
        node.children[first] = split
        return True

    def _locate(
        self, text: str
    ) -> tuple[PatriciaNode, int, bool, str] | None:
        node = self.root
        index = 0
        path = ""
        if text == "":
            return node, 0, True, ""
        while index < len(text):
            child = node.children.get(text[index])
            self.metrics.comparisons += 1
            if child is None:
                return None
            shared = self._common_prefix_length(child.edge, text[index:])
            if shared == 0:
                return None
            if shared < len(child.edge):
                if shared == len(text) - index:
                    return child, len(text), False, path + child.edge
                return None
            path += child.edge
            index += shared
            node = child
        return node, index, True, path

    def _delete_at(self, node: PatriciaNode, remaining: str) -> bool:
        if remaining == "":
            node.is_end = False
            return True
        first = remaining[0]
        child = node.children.get(first)
        if child is None:
            return False
        shared = self._common_prefix_length(child.edge, remaining)
        if shared != len(child.edge):
            return False
        deleted = self._delete_at(child, remaining[shared:])
        if deleted and not child.is_end and not child.children:
            del node.children[first]
            self.metrics.nodes_deleted += 1
        elif deleted:
            self._compress_node(child)
        return deleted

    def _compress(self, node: PatriciaNode) -> None:
        for child in list(node.children.values()):
            self._compress(child)
            self._compress_node(child)

    def _compress_node(self, node: PatriciaNode) -> None:
        if node.is_end or len(node.children) != 1:
            return
        only_key = next(iter(node.children))
        only_child = node.children[only_key]
        node.edge += only_child.edge
        node.children = only_child.children
        node.is_end = only_child.is_end
        self.metrics.nodes_deleted += 1

    def _collect(self, node: PatriciaNode, prefix: str, collected: list[str]) -> None:
        if node.is_end:
            collected.append(prefix)
        for child in node.children.values():
            self._collect(child, prefix + child.edge, collected)

    def _count_nodes(self, node: PatriciaNode) -> int:
        return 1 + sum(self._count_nodes(child) for child in node.children.values())

    def _dot_walk(
        self,
        node: PatriciaNode,
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
            edge_label = child.edge.replace('"', '\\"')
            lines.append(f'  {node_id} -> {child_id} [label="{edge_label}"];')
            self._dot_walk(child, child_id, lines, next_id)
