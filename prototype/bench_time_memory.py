"""Speed and peak-memory comparison of the three engines.

Each cell runs in its own process under /usr/bin/time, so the reported
figures are the wall-clock time and the peak resident set size of that
process as the kernel saw it, not an estimate derived from state counts.

Engines (same as blowup_bench.py):
  cpp        the original DAFNA pipeline: psum/pintersect over the C++
             automata library, then enumeration of shortest words;
  eager      explicit product automaton in Python, 300k-state cap;
  dnf_first  the proposed method: bound-ordered disjunctive decomposition
             with early exit.

Run:  venv/bin/python prototype/bench_time_memory.py
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CELL = os.path.join(ROOT, "prototype", "blowup_bench.py")
TIMEOUT = 120          # seconds per cell
REPEATS = 3            # each cell is run this many times; the median is reported
CELLS = [("imt", 243), ("trp", 2), ("trp", 3), ("trp", 4)]
ENGINES = ["cpp", "eager", "dnf_first"]


def n_patterns(family, scale):
    sys.path.insert(0, os.path.join(ROOT, "prototype"))
    from blowup_bench import family_cell
    return len(family_cell(family, scale)[0])


def run(family, scale, engine):
    cmd = ["/usr/bin/time", "-f", "@@ %e %M",
           "timeout", str(TIMEOUT), sys.executable, CELL,
           "--cell", family, str(scale), engine]
    pr = subprocess.run(cmd, capture_output=True, text=True)
    m = re.search(r"@@ ([\d.]+) (\d+)", pr.stderr)
    secs, kb = (float(m.group(1)), int(m.group(2))) if m else (None, None)
    line = next((l for l in pr.stdout.splitlines() if l.startswith("RESULT ")), None)
    res = json.loads(line[len("RESULT "):]) if line else None
    ok = bool(res and res.get("answer") not in (None, "abandoned"))
    why = ""
    if not ok:
        if secs is not None and secs >= TIMEOUT - 1:
            why = f"таймаут >{TIMEOUT} с"
        elif res:
            why = "отказ: превышен предел состояний"
        else:
            err = (pr.stderr or "").strip().splitlines()
            why = "нехватка памяти" if any("emory" in e for e in err[-3:]) else "отказ"
    return {"seconds": secs, "peak_mb": kb / 1024 if kb else None,
            "answer": res.get("answer") if res else None, "ok": ok, "why": why}


def median(xs):
    xs = sorted(x for x in xs if x is not None)
    return None if not xs else xs[len(xs) // 2]


def main():
    rows = []
    print(f"{'семейство':<10}{'шаблонов':>9}{'движок':>12}{'время':>10}{'пик памяти':>13}  примечание")
    for fam, sc in CELLS:
        n = n_patterns(fam, sc)
        for eng in ENGINES:
            runs = [run(fam, sc, eng) for _ in range(REPEATS)]
            r = dict(runs[0])
            r["seconds"] = median([x["seconds"] for x in runs])
            r["peak_mb"] = median([x["peak_mb"] for x in runs])
            r["all_seconds"] = [x["seconds"] for x in runs]
            r["all_peak_mb"] = [x["peak_mb"] for x in runs]
            r["ok"] = all(x["ok"] for x in runs)
            t = f"{r['seconds']:.1f} с" if r["seconds"] is not None else "—"
            m = f"{r['peak_mb']:.0f} МБ" if r["peak_mb"] is not None else "—"
            print(f"{fam.upper():<10}{n:>9}{eng:>12}{t:>10}{m:>13}  {r['why']}"
                  f"   прогоны: {r['all_seconds']} / {[None if v is None else round(v) for v in r['all_peak_mb']]}",
                  flush=True)
            rows.append({"family": fam, "patterns": n, "engine": eng, **r})
    with open(os.path.join(ROOT, "research", "bench_time_memory.json"), "w") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print("\nsaved research/bench_time_memory.json")


if __name__ == "__main__":
    main()
