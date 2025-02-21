"""Provide a progress bar for parallel task execution."""

from __future__ import annotations

from typing import TYPE_CHECKING

import joblib
from rich.progress import Progress as Super

if TYPE_CHECKING:
    from collections.abc import Callable

    from joblib.parallel import Parallel


# https://github.com/jonghwanhyeon/joblib-progress/blob/main/joblib_progress/__init__.py
class Progress(Super):
    _print_progress: Callable[[Parallel], None] | None = None

    def start(self) -> None:
        """Start the progress display."""
        super().start()

        self._print_progress = joblib.parallel.Parallel.print_progress

        progress = self

        def update_progress(self: joblib.parallel.Parallel) -> None:
            if not progress.task_ids:
                task_id = progress.add_task("", total=None)
            else:
                task_id = progress.task_ids[0]

            progress.update(task_id, completed=self.n_completed_tasks, refresh=True)

            if progress._print_progress:
                progress._print_progress(self)

        joblib.parallel.Parallel.print_progress = update_progress

    def stop(self) -> None:
        """Stop the progress display."""
        if self._print_progress:
            joblib.parallel.Parallel.print_progress = self._print_progress  # type: ignore

        super().stop()
