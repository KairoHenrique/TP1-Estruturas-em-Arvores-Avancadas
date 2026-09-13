"""Executa os experimentos comparativos e grava CSV + gráficos."""

from __future__ import annotations

import csv
import random
import sys
from pathlib import Path
from time import perf_counter
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

from baselines.avl import AVLTree  # noqa: E402
from baselines.bst import BinarySearchTree  # noqa: E402
from common.metrics import Metrics  # noqa: E402
from datasets import (  # noqa: E402
    locality_queries,
    make_words,
    random_points,
    sequential_keys,
    shuffled_keys,
    zipf_queries,
)
from kdtree.kdtree import KDTree, Point  # noqa: E402
from patricia.patricia import PatriciaTree  # noqa: E402
from plots import plot_results  # noqa: E402
from splay.splay import SplayTree  # noqa: E402
from treap.treap import Treap  # noqa: E402
from trie.trie import Trie  # noqa: E402

sys.setrecursionlimit(20000)

SIZES = (1000, 5000, 10000)
SEED = 20260919
CSV_FIELDS = (
    "group",
    "n",
    "structure",
    "pattern",
    "operation",
    "seconds",
    "comparisons",
    "rotations",
    "nodes",
    "memory_bytes",
    "extra",
)


def main() -> None:
    rng = random.Random(SEED)
    rows: list[dict[str, Any]] = []
    rows.extend(run_string_experiments(rng))
    rows.extend(run_ordered_experiments(rng))
    rows.extend(run_kdtree_experiments(rng))
    output_dir = ROOT / "output" / "experiments"
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "resultados.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    plot_results(csv_path, output_dir)
    print(f"CSV em {csv_path}")
    print(f"{len(rows)} linhas experimentais gravadas.")


def run_string_experiments(rng: random.Random) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for size in SIZES:
        words = make_words(size, rng)
        prefixes = [word[:4] for word in words[:: max(1, size // 50)]][:50]
        for name, factory in (("Trie", Trie), ("Patricia", PatriciaTree)):
            metrics = Metrics()
            tree = factory(metrics=metrics)
            rows.append(_measure(name, "strings", size, "prefixos_compartilhados", "insert", metrics, lambda: _insert_all(tree, words), tree))
            rows.append(_measure(name, "strings", size, "prefixos_compartilhados", "search", metrics, lambda: _search_all(tree, words), tree))
            rows.append(
                _measure(
                    name,
                    "strings",
                    size,
                    "prefixos_compartilhados",
                    "prefix_query",
                    metrics,
                    lambda: _prefix_all(tree, prefixes),
                    tree,
                )
            )
            delete_words = words[: size // 5]
            rows.append(
                _measure(
                    name,
                    "strings",
                    size,
                    "prefixos_compartilhados",
                    "delete",
                    metrics,
                    lambda tree=tree, delete_words=delete_words: _delete_all(tree, delete_words),
                    tree,
                )
            )
    return rows


def run_ordered_experiments(rng: random.Random) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    factories: dict[str, Callable[[Metrics], Any]] = {
        "BST": lambda metrics: BinarySearchTree(metrics=metrics),
        "AVL": lambda metrics: AVLTree(metrics=metrics),
        "Splay": lambda metrics: SplayTree(metrics=metrics),
        "Treap": lambda metrics: Treap(metrics=metrics, rng=random.Random(rng.randint(1, 10_000_000))),
    }
    for size in SIZES:
        patterns = {
            "aleatorio": shuffled_keys(size, rng),
            "ordenado": sequential_keys(size),
        }
        for pattern_name, keys in patterns.items():
            for structure_name, factory in factories.items():
                if structure_name in {"BST", "Splay"} and pattern_name == "ordenado" and size > 5000:
                    continue
                metrics = Metrics()
                tree = factory(metrics)
                rows.append(
                    _measure(
                        structure_name,
                        "ordenaveis",
                        size,
                        pattern_name,
                        "insert",
                        metrics,
                        lambda tree=tree, keys=keys: _insert_all(tree, keys),
                        tree,
                    )
                )
                search_keys = list(keys)
                rng.shuffle(search_keys)
                rows.append(
                    _measure(
                        structure_name,
                        "ordenaveis",
                        size,
                        pattern_name,
                        "search",
                        metrics,
                        lambda tree=tree, search_keys=search_keys: _search_all(tree, search_keys),
                        tree,
                    )
                )
                if pattern_name == "aleatorio":
                    zipf = zipf_queries(keys, size, rng)
                    local = locality_queries(keys, size, rng)
                    rows.append(
                        _measure(
                            structure_name,
                            "ordenaveis",
                            size,
                            "zipf",
                            "search",
                            metrics,
                            lambda tree=tree, zipf=zipf: _search_all(tree, zipf),
                            tree,
                        )
                    )
                    rows.append(
                        _measure(
                            structure_name,
                            "ordenaveis",
                            size,
                            "localidade",
                            "search",
                            metrics,
                            lambda tree=tree, local=local: _search_all(tree, local),
                            tree,
                        )
                    )
                delete_keys = keys[: size // 5]
                rows.append(
                    _measure(
                        structure_name,
                        "ordenaveis",
                        size,
                        pattern_name,
                        "delete",
                        metrics,
                        lambda tree=tree, delete_keys=delete_keys: _delete_all(tree, delete_keys),
                        tree,
                    )
                )
    return rows


def run_kdtree_experiments(rng: random.Random) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for size in SIZES:
        for dimensions in (2, 3):
            points = random_points(size, dimensions, rng)
            metrics = Metrics()
            tree = KDTree(dimensions=dimensions, metrics=metrics)
            pattern = f"{dimensions}d"
            rows.append(
                _measure(
                    "KDTree",
                    "espacial",
                    size,
                    pattern,
                    "insert",
                    metrics,
                    lambda tree=tree, points=points: _insert_all(tree, points),
                    tree,
                )
            )
            queries = points[: min(400, size)]
            rows.append(
                _measure(
                    "KDTree",
                    "espacial",
                    size,
                    pattern,
                    "nearest",
                    metrics,
                    lambda tree=tree, queries=queries: _nearest_all(tree, queries),
                    tree,
                    extra=str(len(queries)),
                )
            )
            rows.append(
                _measure(
                    "brute_force",
                    "espacial",
                    size,
                    pattern,
                    "nearest",
                    Metrics(),
                    lambda points=points, queries=queries: _brute_nearest_all(points, queries),
                    tree,
                    extra=str(len(queries)),
                )
            )
            low = tuple(0.0 for _ in range(dimensions))
            high = tuple(250.0 for _ in range(dimensions))
            rows.append(
                _measure(
                    "KDTree",
                    "espacial",
                    size,
                    pattern,
                    "range",
                    metrics,
                    lambda tree=tree, low=low, high=high: tree.range_search(low, high),
                    tree,
                )
            )
            delete_points = points[: size // 5]
            rows.append(
                _measure(
                    "KDTree",
                    "espacial",
                    size,
                    pattern,
                    "delete",
                    metrics,
                    lambda tree=tree, delete_points=delete_points: _delete_all(tree, delete_points),
                    tree,
                )
            )
    return rows


def _measure(
    structure: str,
    group: str,
    size: int,
    pattern: str,
    operation: str,
    metrics: Metrics,
    action: Callable[[], Any],
    tree: Any,
    extra: str = "",
) -> dict[str, Any]:
    metrics.reset()
    started = perf_counter()
    action()
    elapsed = perf_counter() - started
    memory = tree.estimate_memory_bytes() if hasattr(tree, "estimate_memory_bytes") else 0
    nodes = tree.node_count() if hasattr(tree, "node_count") else 0
    return {
        "group": group,
        "n": size,
        "structure": structure,
        "pattern": pattern,
        "operation": operation,
        "seconds": f"{elapsed:.6f}",
        "comparisons": metrics.comparisons,
        "rotations": metrics.rotations,
        "nodes": nodes,
        "memory_bytes": memory,
        "extra": extra,
    }


def _insert_all(tree: Any, items: list[Any]) -> None:
    for item in items:
        tree.insert(item)


def _search_all(tree: Any, items: list[Any]) -> None:
    for item in items:
        tree.search(item)


def _delete_all(tree: Any, items: list[Any]) -> None:
    for item in items:
        tree.delete(item)


def _prefix_all(tree: Any, prefixes: list[str]) -> None:
    for prefix in prefixes:
        tree.starts_with(prefix)
        tree.words_with_prefix(prefix)


def _nearest_all(tree: KDTree, queries: list[Point]) -> None:
    for query in queries:
        tree.nearest(query)


def _brute_nearest_all(points: list[Point], queries: list[Point]) -> None:
    for query in queries:
        _brute_nearest(points, query)


def _brute_nearest(points: list[Point], query: Point) -> Point:
    best = points[0]
    best_dist = _squared(best, query)
    for point in points[1:]:
        distance = _squared(point, query)
        if distance < best_dist:
            best = point
            best_dist = distance
    return best


def _squared(left: Point, right: Point) -> float:
    return sum((a - b) ** 2 for a, b in zip(left, right))


if __name__ == "__main__":
    main()
