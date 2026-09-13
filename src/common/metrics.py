"""Contadores e cronômetro para instrumentar operações das árvores."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from time import perf_counter
from typing import Iterator


@dataclass
class Metrics:
    comparisons: int = 0
    rotations: int = 0
    nodes_created: int = 0
    nodes_deleted: int = 0
    elapsed_seconds: float = 0.0

    def reset(self) -> None:
        self.comparisons = 0
        self.rotations = 0
        self.nodes_created = 0
        self.nodes_deleted = 0
        self.elapsed_seconds = 0.0

    def compare_lt(self, left, right) -> bool:
        self.comparisons += 1
        return left < right

    def compare_eq(self, left, right) -> bool:
        self.comparisons += 1
        return left == right

    def snapshot(self) -> dict[str, float]:
        return {
            "comparisons": self.comparisons,
            "rotations": self.rotations,
            "nodes_created": self.nodes_created,
            "nodes_deleted": self.nodes_deleted,
            "elapsed_seconds": self.elapsed_seconds,
        }


@contextmanager
def timed(metrics: Metrics) -> Iterator[None]:
    started = perf_counter()
    try:
        yield
    finally:
        metrics.elapsed_seconds += perf_counter() - started
