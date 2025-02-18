from __future__ import annotations

import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

from rich.progress import MofNCompleteColumn, Progress

from multiprogress.aio import run

if TYPE_CHECKING:
    from watchfiles import Change


def on_changed(changes: set[tuple[Change, str]]) -> tuple[float, float]:
    for _, path in changes:
        text = Path(path).read_text()
        total, completed = text.split(",")
        break

    return float(total), float(completed)


def main():
    with TemporaryDirectory() as tempdir:
        os.chdir(tempdir)
        arg = Path(__file__).parent.joinpath("task.py").as_posix()
        run([sys.executable, arg], tempdir, on_changed, description="test")

        with Progress(MofNCompleteColumn()) as progress:
            run([sys.executable, arg], tempdir, on_changed, progress=progress)


if __name__ == "__main__":
    main()
