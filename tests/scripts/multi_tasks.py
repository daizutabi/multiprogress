from __future__ import annotations

import random
import time

from rich.progress import (
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TimeElapsedColumn,
)

from multiprogress import multi_tasks_progress


def task(total):
    for i in range(total or 90):
        if total is None:
            yield i
        else:
            yield total, i
        time.sleep(random.random() / 30)


def test_multi_tasks_progress(total: bool, n: int = 4, **kwargs):
    tasks = (task(random.randint(50, 200)) for _ in range(n))
    if total:
        tasks = (task(None), *list(tasks)[:-2], task(None))

    columns = [
        SpinnerColumn(),
        *Progress.get_default_columns(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
    ]

    if total:
        kwargs["main_description"] = "unknown"

    multi_tasks_progress(tasks, *columns, n_jobs=4, **kwargs)


if __name__ == "__main__":
    test_multi_tasks_progress(total=False)
    test_multi_tasks_progress(total=True, transient=False)
    test_multi_tasks_progress(total=False, transient=True)
