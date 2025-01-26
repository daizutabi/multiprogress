from __future__ import annotations

import asyncio
from asyncio.subprocess import PIPE
from typing import TYPE_CHECKING

import watchfiles
from watchfiles import Change

if TYPE_CHECKING:
    from asyncio import Event
    from collections.abc import Callable, Coroutine
    from pathlib import Path
    from typing import Any

    from rich.progress import Progress


def run(
    args: list[str],
    path: Path | str,
    on_changed: Callable[[set[tuple[Change, str]]], tuple[float, float]],
    **kwargs,
) -> int:
    coro = arun(args, path, on_changed, **kwargs)
    return asyncio.run(coro)


async def arun(
    args: list[str],
    path: Path | str,
    on_changed: Callable[[set[tuple[Change, str]]], tuple[float, float]],
    **kwargs,
) -> int:
    async def coro(update: Callable[[float, float], None]) -> int:
        def _on_changed(changes: set[tuple[Change, str]]) -> None:
            total, completed = on_changed(changes)
            update(total, completed)

        return await execute_watch(args, path, _on_changed)

    return await progress(coro, **kwargs)


async def execute_watch(
    args: list[str],
    path: Path | str,
    on_changed: Callable[[set[tuple[Change, str]]], None],
) -> int:
    """Asynchronously execute a command and monitor the output directory.

    This coroutine runs a command with the provided arguments and sets up
    an asynchronous watcher on the specified path. It calls the provided callback
    function with any detected file changes.

    Args:
        args (list[str]): The command-line arguments to run the command.
        path (Path): The path to monitor for file changes.
        on_changed (Callable[[set[tuple[Change, str]]], None]): A callback function
            that takes a set of changes. Each change is represented by a tuple
            containing the type of change and the path to the changed file.

    Returns:
        int: The return code of the process. A return code of 0 indicates
        success, while any non-zero value indicates an error.
    """
    stop_event = asyncio.Event()

    run_task = asyncio.create_task(execute(args, stop_event))
    watch_task = asyncio.create_task(watch(path, stop_event, on_changed))

    try:
        await asyncio.gather(run_task, watch_task)

    finally:
        stop_event.set()
        await run_task
        await watch_task

    return run_task.result()


async def execute(args: list[str], stop_event: Event) -> int:
    """Asynchronously execute a subprocess with the given arguments.

    This coroutine starts a subprocess using the provided command-line arguments
    and waits for it to complete. An asyncio.Event is used to signal when the
    subprocess should be stopped.

    Args:
        args (list[str]): The command-line arguments to execute the subprocess.
        stop_event (Event): An event that, when set, signals the coroutine
            to stop waiting and terminate the subprocess if it is still running.

    Returns:
        int: The return code of the subprocess. A return code of 0 indicates success,
        while any non-zero value indicates an error.

    Raises:
        asyncio.CancelledError: If the coroutine is cancelled before the subprocess
        completes its execution.
    """

    try:
        process = await asyncio.create_subprocess_exec(*args, stdout=PIPE, stderr=PIPE)
        return await process.wait()

    finally:
        stop_event.set()


async def watch(
    path: Path | str,
    stop_event: Event,
    on_changed: Callable[[set[tuple[Change, str]]], None],
    **kwargs,
) -> None:
    """Asynchronously monitor a directory for file changes and execute a callback.

    This coroutine sets up a watcher on the specified path and listens for file
    changes. When a change is detected, it calls the provided callback function
    with the set of changes. The monitoring continues until the stop_event is set.

    Args:
        path (Path): The directory path to monitor for file changes.
        stop_event (Event): An event that, when set, signals the coroutine
            to stop monitoring and terminate.
        callback (Callable[[set[tuple[Change, str]]], None]): A callback function
            that is called with the set of changes detected. Each change is
            represented by a tuple containing the type of change and the path to
            the changed file.
        **kwargs: Additional keyword arguments to pass to the watchfiles.awatch
            function.
    """
    ait = watchfiles.awatch(path, stop_event=stop_event, **kwargs)

    async for changes in ait:
        on_changed(changes)


async def progress(
    func: Callable[[Callable[[float, float], None]], Coroutine[Any, Any, int]],
    description: str = "",
    *,
    progress: Progress | None = None,
    **kwargs,
) -> int:
    """Execute a function with progress monitoring and display updates.

    Wrap the execution of a provided function (typically a long-running
    process) with a visual progress bar. Update the progress bar based on the
    callback from the wrapped function. The progress bar is displayed in
    the console using the 'rich' library.

    Args:
        func (partial[int]): A partial object that, when called, will execute the
            function with pre-defined arguments. The function is expected to accept
            a callback that updates the progress.
        description (str, optional): A description text to display alongside the
            progress bar. Defaults to an empty string.
        refresh_per_second (float): Number of times per second to refresh the progress
            information. Defaults to 1.

    Returns:
        int: The return code from the executed function. A return code of 0 indicates
        success, while any non-zero value indicates an error.
    """
    if progress is None:
        progress = get_default_progress(**kwargs)

    with progress as p:
        task_id = p.add_task(description, total=None)

        def update(total: float, completed: float) -> None:
            p.update(task_id, total=total, completed=completed, refresh=True)

        returncode = await func(update)

        p.update(task_id, total=1, completed=1, refresh=True)

        return returncode


def get_default_progress(**kwargs) -> Progress:
    from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn

    return Progress(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
        **kwargs,
    )
