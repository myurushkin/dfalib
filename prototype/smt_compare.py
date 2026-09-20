"""How far does an SMT string solver (cvc5) get on our queries?

Four experiments, each on the same pattern families as blowup_bench.py:

  E1  existence of a word of length exactly L  (our dnf_first)
  E2  minimal length by shrinking a length bound  (our dnf_min)
  E3  enumerating *all* minimal words with blocking clauses  (our solution graph)
  E4  a query with negation: (U TRP) and not (U GQD), length L

Run:  venv/bin/python prototype/smt_compare.py [--tlimit 120]
"""

from __future__ import annotations

import argparse
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "prototype"))

import cvc5
from cvc5 import Kind

from blowup_bench import family_cell, gqd_regex, gqd_scales

ALPHA = "acgt"


# ---------------------------------------------------------------- regex -> cvc5
class Rx:
    """Tiny parser for the regex subset used by the benchmarks:
    literals, '.', [class], (), |, *, +, ?, {m}, {m,n}."""

    def __init__(self, s, text):
        self.s, self.t, self.i = s, text, 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else ""

    def parse(self):
        r = self.alt()
        assert self.i == len(self.t), self.t
        return r

    def alt(self):
        parts = [self.cat()]
        while self.peek() == "|":
            self.i += 1
            parts.append(self.cat())
        return parts[0] if len(parts) == 1 else self.s.mkTerm(Kind.REGEXP_UNION, *parts)

    def cat(self):
        parts = []
        while self.peek() not in ("", "|", ")"):
            parts.append(self.repeat())
        if not parts:
            return self.s.mkTerm(Kind.STRING_TO_REGEXP, self.s.mkString(""))
        return parts[0] if len(parts) == 1 else self.s.mkTerm(Kind.REGEXP_CONCAT, *parts)

    def repeat(self):
        node = self.atom()
        while True:
            c = self.peek()
            if c == "*":
                self.i += 1; node = self.s.mkTerm(Kind.REGEXP_STAR, node)
            elif c == "+":
                self.i += 1; node = self.s.mkTerm(Kind.REGEXP_PLUS, node)
            elif c == "?":
                self.i += 1; node = self.s.mkTerm(Kind.REGEXP_OPT, node)
            elif c == "{":
                j = self.t.index("}", self.i)
                spec = self.t[self.i + 1:j]; self.i = j + 1
                if "," in spec:
                    lo, hi = (int(v) for v in spec.split(","))
                    node = self.s.mkTerm(self.s.mkOp(Kind.REGEXP_LOOP, lo, hi), node)
                else:
                    node = self.s.mkTerm(self.s.mkOp(Kind.REGEXP_REPEAT, int(spec)), node)
            else:
                return node

    def atom(self):
        c = self.peek()
        if c == "(":
            self.i += 1; r = self.alt(); assert self.peek() == ")"; self.i += 1; return r
        if c == "[":
            j = self.t.index("]", self.i); chars = self.t[self.i + 1:j]; self.i = j + 1
            return self.s.mkTerm(Kind.REGEXP_UNION, *[self.s.mkTerm(Kind.STRING_TO_REGEXP, self.s.mkString(ch)) for ch in chars])
        if c == ".":
            self.i += 1
            return self.s.mkTerm(Kind.REGEXP_UNION, *[self.s.mkTerm(Kind.STRING_TO_REGEXP, self.s.mkString(ch)) for ch in ALPHA])
        self.i += 1
        return self.s.mkTerm(Kind.STRING_TO_REGEXP, self.s.mkString(c))


def solver(tlimit_ms):
    s = cvc5.Solver()
    s.setLogic("QF_SLIA")
    s.setOption("produce-models", "true")
    s.setOption("tlimit-per", str(tlimit_ms))
    return s


def build(s, family, scale, negate_gqd=False, with_gqd=True):
    union_re, _, length = family_cell(family, scale)
    x = s.mkConst(s.getStringSort(), "x")
    alpha = s.mkTerm(Kind.REGEXP_STAR, Rx(s, ".").parse())
    s.assertFormula(s.mkTerm(Kind.STRING_IN_REGEXP, x, alpha))
    motifs = s.mkTerm(Kind.REGEXP_UNION, *[Rx(s, p).parse() for p in union_re])
    s.assertFormula(s.mkTerm(Kind.STRING_IN_REGEXP, x, motifs))
    if with_gqd:
        gqds = s.mkTerm(Kind.REGEXP_UNION, *[Rx(s, gqd_regex(k)).parse() for k in gqd_scales()])
        g = s.mkTerm(Kind.STRING_IN_REGEXP, x, gqds)
        s.assertFormula(s.mkTerm(Kind.NOT, g) if negate_gqd else g)
    return x, length


def check(s):
    t0 = time.perf_counter()
    r = s.checkSat()
    return str(r), time.perf_counter() - t0


def e1_existence(family, scale, tl):
    s = solver(tl)
    x, L = build(s, family, scale)
    s.assertFormula(s.mkTerm(Kind.EQUAL, s.mkTerm(Kind.STRING_LENGTH, x), s.mkInteger(L)))
    r, dt = check(s)
    w = s.getValue(x).getStringValue() if r == "sat" else None
    return r, dt, w


def e2_minimal(family, scale, tl):
    """Shrink the bound: sat with len<=B?  Then B := |model|-1 until unsat."""
    s = solver(tl)
    x, L = build(s, family, scale)
    lenx = s.mkTerm(Kind.STRING_LENGTH, x)
    bound, best, calls, total = L, None, 0, 0.0
    while True:
        s.push()
        s.assertFormula(s.mkTerm(Kind.LEQ, lenx, s.mkInteger(bound)))
        r, dt = check(s); calls += 1; total += dt
        if r == "sat":
            best = s.getValue(x).getStringValue(); bound = len(best) - 1
            s.pop()
        else:
            s.pop()
            return ("unsat" if r == "unsat" else r), best, calls, total


def e2_sweep(family, scale, tl, lo=1):
    """Minimal length by asking len == L for L = lo, lo+1, ... (equality only)."""
    calls, total = 0, 0.0
    for L in range(lo, family_cell(family, scale)[2] + 1):
        s = solver(tl)
        x, _ = build(s, family, scale)
        s.assertFormula(s.mkTerm(Kind.EQUAL, s.mkTerm(Kind.STRING_LENGTH, x), s.mkInteger(L)))
        r, dt = check(s); calls += 1; total += dt
        if r == "sat":
            return L, s.getValue(x).getStringValue(), calls, total
        if r != "unsat":
            return None, f"{r} at L={L}", calls, total
    return None, "none up to bound", calls, total


def e3_enumerate(family, scale, L, seconds, with_gqd=True):
    """All words of length L: blocking clause per model, time-boxed."""
    s = solver(int(seconds * 1000))
    x, _ = build(s, family, scale, with_gqd=with_gqd)
    s.assertFormula(s.mkTerm(Kind.EQUAL, s.mkTerm(Kind.STRING_LENGTH, x), s.mkInteger(L)))
    found, t0 = 0, time.perf_counter()
    while time.perf_counter() - t0 < seconds:
        r = s.checkSat()
        if str(r) != "sat":
            return found, time.perf_counter() - t0, str(r)
        w = s.getValue(x)
        s.assertFormula(s.mkTerm(Kind.NOT, s.mkTerm(Kind.EQUAL, x, w)))
        found += 1
    return found, time.perf_counter() - t0, "timeout"


def e4_negation(family, scale, tl):
    s = solver(tl)
    x, L = build(s, family, scale, negate_gqd=True)
    s.assertFormula(s.mkTerm(Kind.EQUAL, s.mkTerm(Kind.STRING_LENGTH, x), s.mkInteger(L)))
    r, dt = check(s)
    return r, dt, (s.getValue(x).getStringValue() if r == "sat" else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tlimit", type=float, default=120.0, help="seconds per check")
    args = ap.parse_args()
    tl = int(args.tlimit * 1000)

    print("== E1 existence at fixed length (cvc5) ==")
    for fam, sc in (("imt", 243), ("trp", 2), ("trp", 3), ("trp", 4)):
        n = len(family_cell(fam, sc)[0])
        r, dt, w = e1_existence(fam, sc, tl)
        print(f"  {fam}/{n:<4} {r:<8} {dt:7.2f}s  {w!r}", flush=True)

    print("== E2 minimal length by shrinking the bound (cvc5) ==")
    for fam, sc in (("imt", 243), ("trp", 2), ("trp", 3), ("trp", 4)):
        n = len(family_cell(fam, sc)[0])
        r, best, calls, total = e2_minimal(fam, sc, tl)
        print(f"  {fam}/{n:<4} final={r:<8} min_len={len(best) if best else None} "
              f"calls={calls} total={total:7.2f}s", flush=True)

    print("== E2' minimal length by sweeping len == L upward (cvc5) ==")
    for fam, sc, lo in (("trp", 2, 8), ("trp", 3, 12), ("trp", 4, 15), ("imt", 243, 12)):
        n = len(family_cell(fam, sc)[0])
        L, w, calls, total = e2_sweep(fam, sc, tl, lo)
        print(f"  {fam}/{n:<4} min_len={L} witness={w!r} calls={calls} total={total:7.2f}s", flush=True)

    print("== E3 enumerate all words of minimal length (cvc5, blocking clauses, 60 s) ==")
    # (family, scale, L, with_gqd, true count from crosscheck_dfalib / solution graph)
    for fam, sc, L, wg, total in (("trp", 2, 12, False, 155_648), ("trp", 2, 12, True, 16),
                                  ("imt", 27, 11, False, 64)):
        n = len(family_cell(fam, sc)[0])
        found, dt, why = e3_enumerate(fam, sc, L, 60.0, with_gqd=wg)
        rate = found / dt if dt else 0
        print(f"  {fam}/{n:<4}{' and GQD' if wg else ' alone  '} L={L}: {found:,} of {total:,} words in {dt:5.1f}s ({why}); "
              f"{rate:6.1f} words/s -> all would take ~{total / rate / 60 if rate else float('inf'):.0f} min",
              flush=True)

    print("== E4 negation: (U motifs) and not (U GQD), fixed length (cvc5) ==")
    for fam, sc in (("trp", 2), ("trp", 3), ("trp", 4)):
        n = len(family_cell(fam, sc)[0])
        r, dt, w = e4_negation(fam, sc, tl)
        print(f"  {fam}/{n:<4} {r:<8} {dt:7.2f}s  {w!r}", flush=True)


if __name__ == "__main__":
    main()
