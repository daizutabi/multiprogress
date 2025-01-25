import sys
from subprocess import run


def test_progress_bar():
    cp = run([sys.executable, "tests/scripts/parallel.py"], check=False)
    assert cp.returncode == 0
