"""Minimal test runner (no pytest dependency): runs every test_* function."""
import importlib, sys, traceback, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
failed = 0
for path in sorted(pathlib.Path(__file__).parent.glob("tests/test_*.py")):
    mod = importlib.import_module(f"tests.{path.stem}")
    for name in dir(mod):
        if name.startswith("test_"):
            t0 = time.perf_counter()
            try:
                getattr(mod, name)()
                print(f"ok    {name} ({time.perf_counter()-t0:.2f}s)")
            except Exception:
                failed += 1
                print(f"FAIL  {name}")
                traceback.print_exc()
print("FAILED" if failed else "ALL PASSED", failed)
sys.exit(1 if failed else 0)
