from __future__ import annotations

from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn


def get_default_progress(**kwargs) -> Progress:
    return Progress(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
        **kwargs,
    )
