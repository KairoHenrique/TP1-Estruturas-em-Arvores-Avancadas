"""Coloca src/ no sys.path a partir de scripts em demos/ e experiments/."""

from __future__ import annotations

import sys
from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def ensure_imports() -> Path:
    root = project_root()
    src = str(root / "src")
    viz = str(root)
    if src not in sys.path:
        sys.path.insert(0, src)
    if viz not in sys.path:
        sys.path.insert(0, viz)
    return root
