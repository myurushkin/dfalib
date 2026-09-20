"""Correctness tests: everything is cross-checked against brute force."""

import itertools
import random
import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from minstr.nfa import NFA, INF
from minstr.trackers import RegexTracker, CountTracker, RunsTracker, BalancedTracker
from minstr import formula as F
from minstr.search import Problem, find_minimal, all_minimal
from minstr.baseline import find_minimal_eager, build_product
from minstr.query import parse_problem


def words(alphabet, max_len):
    for n in range(max_len + 1):
        for t in itertools.product(alphabet, repeat=n):
            yield "".join(t)


def run(tracker, w):
    s = tracker.start
    for ch in w:
        s = tracker.step(s, ch)
    return s


# ---------------------------------------------------------------- regex ----

def random_regex(rng, alphabet, depth=0):
    r = rng.random()
    if depth > 2 or r < 0.3:
        return rng.choice(list(alphabet) + ["."])
    if r < 0.5:
        return random_regex(rng, alphabet, depth + 1) + random_regex(rng, alphabet, depth + 1)
    if r < 0.65:
        return "(" + random_regex(rng, alphabet, depth + 1) + "|" + random_regex(rng, alphabet, depth + 1) + ")"
    if r < 0.8:
        return "(" + random_regex(rng, alphabet, depth + 1) + ")*"
    if r < 0.9:
        return "(" + random_regex(rng, alphabet, depth + 1) + ")+"
    return "(" + random_regex(rng, alphabet, depth + 1) + ")?"


def test_regex_matches_python_re():
    rng = random.Random(1)
    alphabet = "ab"
    for _ in range(150):
        pat = random_regex(rng, alphabet)
        nfa = NFA(pat, alphabet)
        pyre = re.compile("^(?:" + pat + ")$", re.DOTALL)
        for w in words(alphabet, 5):
            expect = pyre.match(w) is not None
            assert nfa.accepts(run(RegexTracker(pat, alphabet), w)) == expect, (pat, w)


def test_regex_bounds_are_admissible_and_always_is_sound():
    rng = random.Random(2)
    alphabet = "ab"
    for _ in range(100):
        pat = random_regex(rng, alphabet)
        t = RegexTracker(pat, alphabet)
        for w in words(alphabet, 4):
            s = run(t, w)
            # true remaining distance by brute force
            true = INF
            for ext in words(alphabet, 5):
                if t.accepts(run(t, w + ext)):
                    true = len(ext)
                    break
            lb = t.min_remaining(s)
            assert lb <= true, (pat, w, lb, true)
            if true == INF:
                assert lb == INF or lb > 5   # brute force horizon is 5
            if t.always(s):
                for ext in words(alphabet, 3):
                    assert t.accepts(run(t, w + ext)), (pat, w, ext)


def test_bounded_repetition_and_classes():
    t = RegexTracker("[ab]{2,3}c", "abc")
    assert t.accepts(run(t, "abc"))
    assert t.accepts(run(t, "aabc"))
    assert not t.accepts(run(t, "ac"))
    assert not t.accepts(run(t, "aaabc"))


# ------------------------------------------------------------- trackers ----

def brute_count(sub, w):
    n, i = 0, 0
    while True:
        j = w.find(sub, i)
        if j < 0:
            return n
        n += 1
        i = j + len(sub)


def brute_runs(sym, m, w):
    return sum(1 for run_ in re.findall(f"{sym}+", w) if len(run_) >= m)


def brute_balanced(left, right, lo, hi, w):
    # middle is exactly one symbol
    for n in range(lo, hi + 1):
        pat = left * n + "." + right * n
        if re.search(pat, w):
            return True
    return False


def test_count_tracker():
    alphabet = "abc"
    for sub in ["a", "ab", "aa", "aba"]:
        for k in [1, 2, 3]:
            t = CountTracker(sub, k, alphabet)
            for w in words(alphabet, 6):
                assert t.accepts(run(t, w)) == (brute_count(sub, w) >= k), (sub, k, w)


def test_runs_tracker():
    alphabet = "ab"
    for m in [1, 2, 3]:
        for k in [1, 2]:
            t = RunsTracker("a", m, k, alphabet)
            for w in words(alphabet, 7):
                assert t.accepts(run(t, w)) == (brute_runs("a", m, w) >= k), (m, k, w)


def test_balanced_tracker():
    alphabet = "abc"
    for lo, hi in [(1, 1), (1, 2), (2, 3)]:
        t = BalancedTracker("a", ".", "c", lo, hi, alphabet)
        for w in words(alphabet, 7):
            assert t.accepts(run(t, w)) == brute_balanced("a", "c", lo, hi, w), (lo, hi, w)


def test_tracker_bounds_admissible():
    alphabet = "abc"
    trackers = [CountTracker("ab", 2, alphabet), RunsTracker("a", 2, 2, alphabet),
                BalancedTracker("a", ".", "c", 1, 2, alphabet)]
    for t in trackers:
        for w in words(alphabet, 4):
            s = run(t, w)
            true = None
            for ext in words(alphabet, 6):
                if t.accepts(run(t, w + ext)):
                    true = len(ext)
                    break
            assert true is not None
            assert t.min_remaining(s) <= true, (t, w)


def test_tracker_regex_expansions_agree():
    alphabet = "ab"
    trackers = [CountTracker("ab", 2, alphabet), RunsTracker("a", 2, 2, alphabet),
                RunsTracker("a", 1, 3, alphabet), RunsTracker("a", 3, 1, alphabet),
                BalancedTracker("a", ".", "b", 1, 2, alphabet)]
    for t in trackers:
        r = RegexTracker(t.to_regex(), alphabet)
        for w in words(alphabet, 9):
            assert t.accepts(run(t, w)) == r.accepts(run(r, w)), (t, w)


# --------------------------------------------------------------- search ----

def brute_minimal(problem, max_len):
    best = None
    out = []
    for w in words(problem.alphabet, max_len):
        if best is not None and len(w) > best:
            break
        if len(w) < problem.min_len:
            continue
        bits = {i: t.accepts(run(t, w)) for i, t in enumerate(problem.trackers)}
        if F.eval_now(problem.formula, bits):
            best = len(w)
            out.append(w)
    return best, sorted(out)


def random_problem(rng, alphabet):
    trackers = [
        RegexTracker(random_regex(rng, alphabet), alphabet),
        RegexTracker(".*" + random_regex(rng, alphabet) + ".*", alphabet),
        CountTracker(rng.choice(["a", "ab", "ba"]), rng.randint(1, 2), alphabet),
        RunsTracker("a", rng.randint(1, 2), rng.randint(1, 2), alphabet),
        BalancedTracker("a", ".", "b", 1, rng.randint(1, 2), alphabet),
    ]
    leaves = [F.leaf(i) for i in range(len(trackers))]

    def rf(d=0):
        r = rng.random()
        if d > 1 or r < 0.35:
            l = rng.choice(leaves)
            return F.NOT(l) if rng.random() < 0.25 else l
        if r < 0.7:
            return F.AND(rf(d + 1), rf(d + 1))
        return F.OR(rf(d + 1), rf(d + 1))

    return Problem(trackers, rf(), alphabet, max_len=7)


def test_search_matches_brute_force():
    rng = random.Random(3)
    alphabet = "ab"
    checked = 0
    for _ in range(120):
        p = random_problem(rng, alphabet)
        best, all_words = brute_minimal(p, 7)
        s, _ = find_minimal(p)
        if best is None:
            assert s is None, (F.pretty(p.formula, [t.name for t in p.trackers]), s)
            continue
        assert s is not None and len(s) == best and s in all_words
        g, _ = all_minimal(p)
        assert g.count() == len(all_words)
        assert sorted(g.enumerate()) == all_words
        assert g.sample() in all_words
        checked += 1
    assert checked > 30


def test_eager_baseline_agrees_with_lazy():
    rng = random.Random(4)
    alphabet = "ab"
    for _ in range(60):
        p = random_problem(rng, alphabet)
        s, _ = find_minimal(p)
        e, st = find_minimal_eager(p.trackers, p.formula, alphabet, max_len=7)
        assert st.failed is None
        assert (s is None) == (e is None)
        if s is not None:
            assert len(s) == len(e)
            dfa, _ = build_product(p.trackers, p.formula, alphabet)
            g, _ = all_minimal(p)
            assert dfa.count_shortest(len(s)) == g.count()


def test_length_window():
    alphabet = "ab"
    t = RegexTracker("a*", alphabet)
    p = Problem([t], F.leaf(0), alphabet, min_len=3, max_len=5)
    s, _ = find_minimal(p)
    assert s == "aaa"
    p = Problem([t], F.AND(F.leaf(0), F.leaf(0)), alphabet, min_len=6, max_len=5)
    assert find_minimal(p)[0] is None


def test_query_language_roundtrip():
    text = """
    alphabet: abcd
    length: 0..20
    A = .*aa.*
    B = count("cc") >= 3
    C = runs(a, 2) >= 2
    D = balanced(a, ., c, 1, 3)
    E = <A>b
    query: A and (B or not C) and D
    """
    p, names = parse_problem(text)
    assert names == ["A", "B", "C", "D", "E"]
    s, _ = find_minimal(p)
    assert s is not None and "aa" in s
    e, st = find_minimal_eager(p.trackers, p.formula, p.alphabet, max_len=20)
    assert len(e) == len(s)


def test_astar_matches_plain_bfs_on_medium_problems():
    """Beyond the brute-force horizon: A* must equal uninformed BFS in length."""
    rng = random.Random(7)
    alphabet = "abc"
    for _ in range(40):
        k = rng.randint(2, 4)
        trackers = [CountTracker(rng.choice(["ab", "ca", "bb"]), rng.randint(2, 5), alphabet),
                    RunsTracker(rng.choice("abc"), rng.randint(1, 3), rng.randint(2, 4), alphabet),
                    BalancedTracker("a", ".", "c", 1, rng.randint(1, 3), alphabet),
                    RegexTracker(".*" + rng.choice(["abc", "cab", "bca"]) + ".*", alphabet)]
        f = F.AND(*[F.leaf(i) for i in range(k)])
        p = Problem(trackers, f, alphabet, max_len=40)
        s, _ = find_minimal(p)
        q = Problem(trackers, f, alphabet, max_len=40)
        real_bound = q.bound
        q.bound = lambda st: INF if real_bound(st) == INF else 0
        b, _ = find_minimal(q)
        assert (s is None) == (b is None)
        if s is not None:
            assert len(s) == len(b), (F.pretty(f, [t.name for t in trackers]), s, b)
