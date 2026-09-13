"""Geração de conjuntos de dados para os três grupos experimentais."""

from __future__ import annotations

import random
from collections.abc import Sequence


STRING_PREFIXES = ("pre", "pro", "par", "com", "con", "tra", "uni", "inf", "est", "alg")


def make_words(count: int, rng: random.Random) -> list[str]:
    words: set[str] = set()
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    while len(words) < count:
        prefix = rng.choice(STRING_PREFIXES)
        suffix_len = rng.randint(4, 9)
        suffix = "".join(rng.choice(alphabet) for _ in range(suffix_len))
        words.add(prefix + suffix)
    return list(words)


def shuffled_keys(count: int, rng: random.Random) -> list[int]:
    keys = list(range(count))
    rng.shuffle(keys)
    return keys


def sequential_keys(count: int) -> list[int]:
    return list(range(count))


def zipf_queries(keys: Sequence[int], query_count: int, rng: random.Random, exponent: float = 1.15) -> list[int]:
    ranked = list(keys)
    weights = [1.0 / ((index + 1) ** exponent) for index in range(len(ranked))]
    return rng.choices(ranked, weights=weights, k=query_count)


def locality_queries(keys: Sequence[int], query_count: int, rng: random.Random, window: int = 16) -> list[int]:
    if not keys:
        return []
    hot = list(keys[: max(1, len(keys) // 10)])
    queries: list[int] = []
    current = rng.choice(hot)
    for _ in range(query_count):
        queries.append(current)
        if rng.random() < 0.75:
            offset = rng.randint(0, min(window, len(hot) - 1))
            current = hot[offset]
        else:
            current = rng.choice(keys)
    return queries


def random_points(count: int, dimensions: int, rng: random.Random, span: float = 1000.0) -> list[tuple[float, ...]]:
    points: set[tuple[float, ...]] = set()
    while len(points) < count:
        point = tuple(round(rng.uniform(0.0, span), 4) for _ in range(dimensions))
        points.add(point)
    return list(points)
