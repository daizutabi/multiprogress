"""Context managers and functions for parallel task execution with progress.

Provide context managers and functions to facilitate the execution
of tasks in parallel while displaying progress updates.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import joblib
from rich.progress import Progress

from .progress_table import ProgressTable

if TYPE_CHECKING:
    from collections.abc import Iterable

    from joblib.parallel import Parallel
    from rich.progress import ProgressColumn


def multi_tasks_progress(  # noqa: PLR0913
    iterables: Iterable[Iterable[int | tuple[int, int]]],
    *columns: ProgressColumn | str,
    n_jobs: int = -1,
    description: str = "#{:0>3}",
    main_description: str = "main",
    transient: bool | None = None,
    parallel: Parallel | None = None,
    use_table: bool = False,
    **kwargs,
) -> None:
    """Render auto-updating progress bars for multiple tasks concurrently.

    Args:
        iterables (Iterable[Iterable[int | tuple[int, int]]]): A collection of
            iterables, each representing a task. Each iterable can yield
            integers (completed) or tuples of integers (completed, total).
        *columns (ProgressColumn | str): Additional columns to display in the
            progress bars.
        n_jobs (int, optional): Number of jobs to run in parallel. Defaults to
            -1, which means using all processors.
        description (str, optional): Format string for describing tasks. Defaults to
            "#{:0>3}".
        main_description (str, optional): Description for the main task.
            Defaults to "main".
        transient (bool | None, optional): Whether to remove the progress bar
            after completion. Defaults to None.
        parallel (Parallel | None, optional): A Parallel instance to use.
            Defaults to None.
        use_table (bool, optional): Whether to use a table to display the
            progress bars. Defaults to False.
        **kwargs: Additional keyword arguments passed to the Progress instance.

    Returns:
        None

    """
    if not columns:
        columns = Progress.get_default_columns()

    cls = ProgressTable if use_table else Progress

    with cls(*columns, transient=transient or False, **kwargs) as progress:
        iterables = list(iterables)
        n = len(iterables)
        task_main = progress.add_task(main_description, total=n)

        task_ids = [
            progress.add_task(description.format(i), start=False, total=None)
            for i in range(n)
        ]

        def update(i: int) -> None:
            task_id = task_ids[i]

            progress.start_task(task_id)

            total = completed = None

            for index in iterables[i]:
                if isinstance(index, tuple):
                    total, completed = index
                else:
                    total, completed = None, index

                progress.update(task_id, total=total, completed=completed)

            progress.update(task_id, total=total, completed=total, refresh=True)
            progress.update(task_main, advance=1, refresh=True)

            if transient is not False:
                progress.remove_task(task_id)

        parallel = parallel or joblib.Parallel(n_jobs=n_jobs, prefer="threads")
        parallel(joblib.delayed(update)(i) for i in range(n))
