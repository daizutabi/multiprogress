import sys
from subprocess import run


def test_aio():
    cp = run([sys.executable, "tests/scripts/aio.py"], check=False)
    assert cp.returncode == 0
