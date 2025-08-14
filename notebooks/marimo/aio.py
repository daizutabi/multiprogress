import marimo

__generated_with = "0.14.17"
app = marimo.App(width="medium")


@app.cell
def _():
    import sys
    from pathlib import Path

    from watchfiles import Change

    from multiprogress.marimo import arun

    return Change, Path, arun, sys


@app.cell
def _(Change, Path):
    def on_changed(changes: set[tuple[Change, str]]) -> tuple[int, int]:
        total = completed = 0

        for _, path in changes:
            text = Path(path).read_text()
            total, completed = text.split(",")
            break
        return int(total), int(completed)
    return (on_changed,)


@app.cell
async def _(arun, on_changed, sys):
    arg = "../../tests/scripts/task.py"
    _=await arun([sys.executable, arg], "a.txt", on_changed)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
