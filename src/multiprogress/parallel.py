"""Context managers and functions for parallel task execution with progress.

Provide context managers and functions to facilitate the execution
of tasks in parallel while displaying progress updates.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, TypeVar

import joblib
from rich.progress import Progress

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from joblib.parallel import Parallel
    from rich.progress import ProgressColumn, TaskID


# https://github.com/jonghwanhyeon/joblib-progress/blob/main/joblib_progress/__init__.py
@contextmanager
def joblib_progress(
    progress: Progress,
    task_id: TaskID,
) -> Iterator[Progress]:
    """Context manager for tracking progress using Joblib with Rich's Progress bar.

    Args:
        progress (Progress): A Progress instance for managing the progress bar.
        task_id (TaskID): A task ID to update.

    Yields:
        Progress: A Progress instance for managing the progress bar.

    """
    print_progress = joblib.parallel.Parallel.print_progress

    def update_progress(self: joblib.parallel.Parallel) -> None:
        progress.update(task_id, completed=self.n_completed_tasks, refresh=True)
        return print_progress(self)

    joblib.parallel.Parallel.print_progress = update_progress

    try:
        yield progress

    finally:
        joblib.parallel.Parallel.print_progress = print_progress


T = TypeVar("T")
U = TypeVar("U")


@contextmanager
def parallel_progress(
    *columns: ProgressColumn | str,
    description: str = "",
    total: int | None = None,
    **kwargs,
) -> Iterator[None]:
    """Context manager for parallel task execution with progress.

    Args:
        *columns (ProgressColumn | str): Columns to display in the progress bar.
        description (str, optional): A description for the progress bar.
            Defaults to "".
        total (int | None, optional): The total number of items to process.
            Defaults to None.
        **kwargs: Additional keyword arguments passed to the Progress instance.

    Returns:
        list[U]: A list of results from applying the function to each item in
        the iterable.

    """
    with Progress(*columns, **kwargs) as progress:
        task_id = progress.add_task(description, total=total)

        with joblib_progress(progress, task_id):
            yield


def multi_tasks_progress(  # noqa: PLR0913
    iterables: Iterable[Iterable[int | tuple[int, int]]],
    *columns: ProgressColumn | str,
    n_jobs: int = -1,
    description: str = "#{:0>3}",
    main_description: str = "main",
    transient: bool | None = None,
    parallel: Parallel | None = None,
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
        **kwargs: Additional keyword arguments passed to the Progress instance.

    Returns:
        None

    """
    if not columns:
        columns = Progress.get_default_columns()

    iterables = list(iterables)

    with Progress(*columns, transient=transient or False, **kwargs) as progress:
        task_main = progress.add_task(main_description, total=None)

        task_ids = [
            progress.add_task(description.format(i), start=False, total=None)
            for i in range(len(iterables))
        ]

        total = {}
        completed = {}

        def update(i: int) -> None:
            completed[i] = 0
            total[i] = None
            progress.start_task(task_ids[i])

            for index in iterables[i]:
                if isinstance(index, tuple):
                    completed[i], total[i] = index[0] + 1, index[1]
                else:
                    completed[i] = index + 1

                progress.update(task_ids[i], total=total[i], completed=completed[i])

                if all(t is not None for t in total.values()):
                    t = sum(total.values())
                else:
                    t = None
                c = sum(completed.values())
                progress.update(task_main, total=t, completed=c)

            if transient is not False:
                progress.remove_task(task_ids[i])

        parallel = parallel or joblib.Parallel(n_jobs=n_jobs, prefer="threads")
        parallel(joblib.delayed(update)(i) for i in range(len(iterables)))
