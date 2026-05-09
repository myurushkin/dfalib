"""
Subprocess-isolated benchmark runner.

run_bench(*args) runs _bench_runner.py in a fresh child process and returns
the JSON result dict. peak_rss_kb is reported by the runner itself via
/proc/self/status VmPeak, giving the true peak RSS of that isolated process.

Each measurement runs in its own Python process, so allocations from prior
measurements cannot inflate the reading.
"""

import json
import pathlib
import subprocess

_RUNNER = pathlib.Path(__file__).with_name("_bench_runner.py")
_VENV_PYTHON = "/home/ilya/storage/pappers/dfa_pappepr/.venv/bin/python"


def run_bench(*args: str) -> dict:
    """Run _bench_runner.py in a subprocess, return JSON dict with peak_rss_kb."""
    proc = subprocess.run(
        [_VENV_PYTHON, str(_RUNNER), *args],
        capture_output=True,
        text=True,
        timeout=600,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"_bench_runner failed:\n{proc.stderr.strip()}")
    # dafna may print debug lines to stdout; JSON is always the last line
    last_line = proc.stdout.strip().splitlines()[-1]
    return json.loads(last_line)
