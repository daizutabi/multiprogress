from __future__ import annotations

import random
import time

from rich.progress import MofNCompleteColumn, SpinnerColumn, TimeElapsedColumn

from multiprogress.multi_tasks import Progress, ProgressTable


def task(total):
    for i in range(total or 90):
        if total is None:
            yield i
        else:
            yield total, i
        time.sleep(random.random() / 30)


def test_multi_tasks_progress(n: int = 4, use_table: bool = False, **kwargs):
    tasks = (task(random.randint(300, 500) if k else None) for k in range(n))
    columns = [
        SpinnerColumn(),
        *Progress.get_default_columns(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
    ]

    cls = ProgressTable if use_table else Progress

    with cls(*columns, **kwargs) as progress:
        if cls is ProgressTable:
            progress.add_task("main", total=n)
        progress.start_tasks(tasks)


if __name__ == "__main__":
    test_multi_tasks_progress()
    test_multi_tasks_progress(transient=True)
