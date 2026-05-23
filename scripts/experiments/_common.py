import os
import sys
import time
import tracemalloc

DFALIB_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
if DFALIB_SRC not in sys.path:
    sys.path.insert(0, DFALIB_SRC)

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EXPERIMENTS_DIR = os.path.join(REPO_ROOT, "experiments")


def measure(callable_):
    tracemalloc.start()
    t0 = time.perf_counter()
    result = callable_()
    elapsed = time.perf_counter() - t0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, elapsed, peak


def write_csv(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(",".join(header) + "\n")
        for r in rows:
            f.write(",".join(str(x) for x in r) + "\n")
    print(f"wrote {path} ({len(rows)} rows)")
