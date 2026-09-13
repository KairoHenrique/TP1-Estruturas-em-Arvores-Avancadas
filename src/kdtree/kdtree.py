"""KD-Tree para pontos k-dimensionais: inserção, NN, range e remoção."""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass

from common.metrics import Metrics

Point = tuple[float, ...]


@dataclass
class KDNode:
    point: Point
    left: KDNode | None = None
    right: KDNode | None = None
    axis: int = 0


class KDTree:
    def __init__(self, dimensions: int = 2, metrics: Metrics | None = None) -> None:
        if dimensions < 1:
            raise ValueError("KD-Tree exige pelo menos 1 dimensão.")
        self.dimensions = dimensions
        self.metrics = metrics or Metrics()
        self.root: KDNode | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def insert(self, point: Point) -> bool:
        self._validate(point)
        if self.search(point):
            return False
        self.root = self._insert(self.root, point, 0)
        self._size += 1
        return True

    def search(self, point: Point) -> bool:
        self._validate(point)
        node = self.root
        depth = 0
        while node is not None:
            if self._same_point(node.point, point):
                return True
            axis = depth % self.dimensions
            if self._less_on_axis(point, node.point, axis):
                node = node.left
            else:
                node = node.right
            depth += 1
        return False

    def delete(self, point: Point) -> bool:
        self._validate(point)
        if not self.search(point):
            return False
        self.root = self._delete(self.root, point, 0)
        self._size -= 1
        return True

    def nearest(self, query: Point) -> Point | None:
        self._validate(query)
        if self.root is None:
            return None
        best: list[Point | None] = [None]
        best_dist = [math.inf]
        self._nearest(self.root, query, 0, best, best_dist)
        return best[0]

    def range_search(self, low: Point, high: Point) -> list[Point]:
        self._validate(low)
        self._validate(high)
        found: list[Point] = []
        self._range(self.root, low, high, 0, found)
        return found

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

    def estimate_memory_bytes(self) -> int:
        total = 0
        stack = [self.root] if self.root else []
        while stack:
            node = stack.pop()
            if node is None:
                continue
            total += sys.getsizeof(node) + sys.getsizeof(node.point)
            stack.append(node.left)
            stack.append(node.right)
        return total

    def to_dot(self) -> str:
        lines = ["digraph KDTree {", '  node [shape=box, fontname="Helvetica"];']
        if self.root is None:
            lines.append('  empty [label="∅", shape=plaintext];')
        else:
            self._dot_walk(self.root, "n0", lines, [1])
        lines.append("}")
        return "\n".join(lines)

    def partition_segments(
        self,
        bounds: tuple[float, float, float, float] = (0.0, 10.0, 0.0, 10.0),
    ) -> list[tuple[tuple[float, float], tuple[float, float]]]:
        """Retorna segmentos das retas de partição em 2D para visualização."""
        if self.dimensions != 2 or self.root is None:
            return []
        xmin, xmax, ymin, ymax = bounds
        segments: list[tuple[tuple[float, float], tuple[float, float]]] = []
        self._collect_segments(self.root, xmin, xmax, ymin, ymax, segments)
        return segments

    def points(self) -> list[Point]:
        collected: list[Point] = []
        self._collect_points(self.root, collected)
        return collected

    def _validate(self, point: Point) -> None:
        if len(point) != self.dimensions:
            raise ValueError(f"Ponto deve ter {self.dimensions} coordenadas.")

    def _same_point(self, left: Point, right: Point) -> bool:
        self.metrics.comparisons += 1
        return left == right

    def _less_on_axis(self, left: Point, right: Point, axis: int) -> bool:
        self.metrics.comparisons += 1
        return left[axis] < right[axis]

    def _insert(self, node: KDNode | None, point: Point, depth: int) -> KDNode:
        if node is None:
            self.metrics.nodes_created += 1
            return KDNode(point=point, axis=depth % self.dimensions)
        axis = depth % self.dimensions
        if self._less_on_axis(point, node.point, axis):
            node.left = self._insert(node.left, point, depth + 1)
        else:
            node.right = self._insert(node.right, point, depth + 1)
        return node

    def _delete(self, node: KDNode | None, point: Point, depth: int) -> KDNode | None:
        if node is None:
            return None
        axis = depth % self.dimensions
        if self._same_point(node.point, point):
            self.metrics.nodes_deleted += 1
            if node.right is not None:
                replacement = self._find_min(node.right, axis, depth + 1)
                node.point = replacement.point
                node.right = self._delete(node.right, replacement.point, depth + 1)
                return node
            if node.left is not None:
                replacement = self._find_min(node.left, axis, depth + 1)
                node.point = replacement.point
                node.right = self._delete(node.left, replacement.point, depth + 1)
                node.left = None
                return node
            return None
        if self._less_on_axis(point, node.point, axis):
            node.left = self._delete(node.left, point, depth + 1)
        else:
            node.right = self._delete(node.right, point, depth + 1)
        return node

    def _find_min(self, node: KDNode, dim: int, depth: int) -> KDNode:
        if node is None:
            raise ValueError("Subárvore vazia em find_min.")
        axis = depth % self.dimensions
        if axis == dim:
            if node.left is None:
                return node
            return self._find_min(node.left, dim, depth + 1)
        candidates = [node]
        if node.left is not None:
            candidates.append(self._find_min(node.left, dim, depth + 1))
        if node.right is not None:
            candidates.append(self._find_min(node.right, dim, depth + 1))
        return min(candidates, key=lambda item: item.point[dim])

    def _nearest(
        self,
        node: KDNode | None,
        query: Point,
        depth: int,
        best: list[Point | None],
        best_dist: list[float],
    ) -> None:
        if node is None:
            return
        distance = self._squared_distance(query, node.point)
        if distance < best_dist[0]:
            best_dist[0] = distance
            best[0] = node.point
        axis = depth % self.dimensions
        diff = query[axis] - node.point[axis]
        self.metrics.comparisons += 1
        first, second = (node.left, node.right) if diff < 0 else (node.right, node.left)
        self._nearest(first, query, depth + 1, best, best_dist)
        if diff * diff < best_dist[0]:
            self._nearest(second, query, depth + 1, best, best_dist)

    def _range(
        self,
        node: KDNode | None,
        low: Point,
        high: Point,
        depth: int,
        found: list[Point],
    ) -> None:
        if node is None:
            return
        if self._inside(node.point, low, high):
            found.append(node.point)
        axis = depth % self.dimensions
        if low[axis] <= node.point[axis]:
            self._range(node.left, low, high, depth + 1, found)
        if high[axis] >= node.point[axis]:
            self._range(node.right, low, high, depth + 1, found)

    def _inside(self, point: Point, low: Point, high: Point) -> bool:
        self.metrics.comparisons += 1
        return all(low[i] <= point[i] <= high[i] for i in range(self.dimensions))

    def _squared_distance(self, left: Point, right: Point) -> float:
        return sum((a - b) ** 2 for a, b in zip(left, right))

    def _collect_points(self, node: KDNode | None, collected: list[Point]) -> None:
        if node is None:
            return
        collected.append(node.point)
        self._collect_points(node.left, collected)
        self._collect_points(node.right, collected)

    def _collect_segments(
        self,
        node: KDNode | None,
        xmin: float,
        xmax: float,
        ymin: float,
        ymax: float,
        segments: list[tuple[tuple[float, float], tuple[float, float]]],
    ) -> None:
        if node is None:
            return
        x, y = node.point[0], node.point[1]
        if node.axis == 0:
            segments.append(((x, ymin), (x, ymax)))
            self._collect_segments(node.left, xmin, x, ymin, ymax, segments)
            self._collect_segments(node.right, x, xmax, ymin, ymax, segments)
        else:
            segments.append(((xmin, y), (xmax, y)))
            self._collect_segments(node.left, xmin, xmax, ymin, y, segments)
            self._collect_segments(node.right, xmin, xmax, y, ymax, segments)

    def _dot_walk(
        self,
        node: KDNode,
        node_id: str,
        lines: list[str],
        next_id: list[int],
    ) -> None:
        coords = ", ".join(f"{value:g}" for value in node.point)
        axis_name = "x" if node.axis == 0 else "y" if node.axis == 1 else f"d{node.axis}"
        lines.append(f'  {node_id} [label="({coords})\\n eix={axis_name}"];')
        for child, side in ((node.left, "L"), (node.right, "R")):
            if child is None:
                continue
            child_id = f"n{next_id[0]}"
            next_id[0] += 1
            lines.append(f'  {node_id} -> {child_id} [label="{side}"];')
            self._dot_walk(child, child_id, lines, next_id)
