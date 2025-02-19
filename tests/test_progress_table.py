import sys
from subprocess import run


def test_progress_table():
    cp = run([sys.executable, "tests/scripts/progress_table.py"], check=False)
    assert cp.returncode == 0
