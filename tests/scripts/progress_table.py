from __future__ import annotations

from multi_tasks import test_multi_tasks_progress

if __name__ == "__main__":
    test_multi_tasks_progress(total=False, n=10, use_table=True)
    test_multi_tasks_progress(total=False, n=10, transient=False, use_table=True)
