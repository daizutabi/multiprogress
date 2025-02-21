from __future__ import annotations

from multi_tasks import test_multi_tasks_progress

if __name__ == "__main__":
    test_multi_tasks_progress(n=8, use_table=True)
    test_multi_tasks_progress(n=8, transient=True, use_table=True)
