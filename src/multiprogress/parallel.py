"""Context managers and functions for parallel task execution with progress.

Provide context managers and functions to facilitate the execution
of tasks in parallel while displaying progress updates.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

import joblib
from rich.progress import Progress

if TYPE_CHECKING:
    from collections.abc import Iterator

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
