"""Provide a progress bar for parallel task execution."""

from __future__ import annotations

from typing import TYPE_CHECKING

import joblib
from rich.progress import Progress as Super

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    from joblib.parallel import Parallel
    from rich.progress import TaskID


# https://github.com/jonghwanhyeon/joblib-progress/blob/main/joblib_progress/__init__.py
class Progress(Super):
    _print_progress: Callable[[Parallel], None] | None = None

    def start(self) -> None:
        super().start()

        self._print_progress = joblib.parallel.Parallel.print_progress

    def add_task(
        self,
        description: str,
        start: bool = True,
        total: float | None = 100.0,
        completed: int = 0,
        visible: bool = True,
        **fields: Any,
    ) -> TaskID:
        task_id = super().add_task(
            description,
            start=start,
            total=total,
            completed=completed,
            visible=visible,
            **fields,
        )

        progress = self

        def update_progress(self: joblib.parallel.Parallel) -> None:
            progress.update(task_id, completed=self.n_completed_tasks, refresh=True)

            if progress._print_progress:
                progress._print_progress(self)

        joblib.parallel.Parallel.print_progress = update_progress

        return task_id

    def stop(self) -> None:
        if self._print_progress:
            joblib.parallel.Parallel.print_progress = self._print_progress  # type: ignore

        super().stop()
