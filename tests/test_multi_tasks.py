import sys
from subprocess import run


def test_multi_tasks():
    cp = run([sys.executable, "tests/scripts/multi_tasks.py"], check=False)
    assert cp.returncode == 0
