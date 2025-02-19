from __future__ import annotations

import time

from joblib import Parallel, delayed
from rich.progress import (
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TimeElapsedColumn,
)

from multiprogress import parallel_progress


def test_parallel_progress(**kwargs):
    def func(x: int) -> str:
        time.sleep(1)
        return f"result: {x}"

    columns = [
        SpinnerColumn(),
        *Progress.get_default_columns(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
    ]

    it = list(range(24))
    with parallel_progress(*columns, total=len(it), **kwargs):
        Parallel(n_jobs=-1)(delayed(func)(x) for x in it)


if __name__ == "__main__":
    test_parallel_progress()
    test_parallel_progress(transient=True)
