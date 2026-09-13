"""Backend matplotlib sem janela (Linux headless, SSH, laboratório)."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


def configure() -> None:
    os.environ.setdefault("MPLBACKEND", "Agg")
    cache = Path(tempfile.gettempdir()) / "matplotlib-tp1-aeds2"
    try:
        cache.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault("MPLCONFIGDIR", str(cache))
    except OSError:
        pass
    import matplotlib

    matplotlib.use("Agg", force=True)
