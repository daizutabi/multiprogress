import time
from pathlib import Path


def main():
    total = 30

    for completed in range(1, total + 1):
        time.sleep(0.2)
        Path("a.txt").write_text(f"{total},{completed}")


if __name__ == "__main__":
    main()
