"""Is the cvc5 comparison fair to cvc5?  Re-run the decisive queries under the
solver options that target exactly our workload, instead of the defaults:

  re-elim=agg          eliminate regexes with loops/counters via length arithmetic
  strings-fmf=true     finite-model finding: look for short models first
  strings-alpha-card=4 tell the solver the alphabet has four letters

Two questions per cell: existence at the loose length L (E1) and the true
minimal length by shrinking the bound with push/pop (E2).  60 s per check.

Run:  venv/bin/python prototype/smt_options.py
"""
from __future__ import annotations
import os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "prototype"))
import cvc5
from cvc5 import Kind
from smt_compare import build, check

TL = 60_000
CELLS = [("imt", 243), ("trp", 40), ("trp", 144), ("trp", 544)]
CONFIGS = {
    "default":            {},
    "re-elim=agg":        {"re-elim": "agg"},
    "fmf":                {"strings-fmf": "true"},
    "fmf+re-elim=agg":    {"strings-fmf": "true", "re-elim": "agg"},
    "fmf+alpha4":         {"strings-fmf": "true", "strings-alpha-card": "4"},
    "all":                {"strings-fmf": "true", "re-elim": "agg", "strings-alpha-card": "4",
                           "strings-exp": "true"},
}

def solver(opts):
    s = cvc5.Solver()
    s.setLogic("QF_SLIA")
    s.setOption("produce-models", "true")
    s.setOption("tlimit-per", str(TL))
    for k, v in opts.items():
        s.setOption(k, v)
    return s

def e1(fam, sc, opts):
    s = solver(opts); x, L = build(s, fam, sc)
    s.assertFormula(s.mkTerm(Kind.EQUAL, s.mkTerm(Kind.STRING_LENGTH, x), s.mkInteger(L)))
    r, dt = check(s); return r, dt

def e2(fam, sc, opts):
    s = solver(opts); x, L = build(s, fam, sc)
    lenx = s.mkTerm(Kind.STRING_LENGTH, x)
    bound, best, total, t0 = L, None, 0.0, time.perf_counter()
    while True:
        s.push(); s.assertFormula(s.mkTerm(Kind.LEQ, lenx, s.mkInteger(bound)))
        r, dt = check(s); total += dt
        if r == "sat":
            best = s.getValue(x).getStringValue(); bound = len(best) - 1; s.pop()
        else:
            s.pop()
            return ("min=%d" % len(best) if r == "unsat" and best else
                    ("%s, лучшее %s" % (r, len(best) if best else "—"))), total

print(f"{'ячейка':<9}{'конфигурация':<18}{'E1 существование':>22}{'E2 минимум':>26}", flush=True)
for fam, sc in CELLS:
    for name, opts in CONFIGS.items():
        try:
            r1, t1 = e1(fam, sc, opts)
            r2, t2 = e2(fam, sc, opts)
            print(f"{fam.upper()+'/'+str(sc):<9}{name:<18}{r1+' '+f'{t1:.1f}с':>22}{r2+' '+f'{t2:.1f}с':>26}", flush=True)
        except Exception as e:
            print(f"{fam.upper()+'/'+str(sc):<9}{name:<18}  ошибка: {str(e)[:60]}", flush=True)
