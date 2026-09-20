import itertools, random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from minstr import formula as F
from minstr.search import Problem
from minstr.trackers import RegexTracker, CountTracker, BalancedTracker
from minstr.optimize import FeasibleGraph, uniform_search, cross_entropy, window_mcmc, _window_fillings

A = "abc"


def feasible_brute(problem, length):
    out = []
    for t in itertools.product(A, repeat=length):
        w = "".join(t)
        bits = {}
        for i, tr in enumerate(problem.trackers):
            s = tr.start
            for ch in w:
                s = tr.step(s, ch)
            bits[i] = tr.accepts(s)
        if F.eval_now(problem.formula, bits):
            out.append(w)
    return out


def make_problem():
    trackers = [RegexTracker(".*ab.*", A), CountTracker("ca", 2, A),
                BalancedTracker("a", ".", "c", 1, 2, A), RegexTracker(".*bb.*", A)]
    f = F.AND(F.leaf(0), F.leaf(1), F.leaf(2), F.NOT(F.leaf(3)))
    return Problem(trackers, f, A, max_len=9)


def test_feasible_graph_counts_and_samples():
    p = make_problem()
    words = set(feasible_brute(p, 8))
    g = FeasibleGraph(p, 8)
    assert g.count() == len(words)
    rng = random.Random(0)
    seen = set()
    for _ in range(300):
        w = g.sample(rng)
        assert w in words
        seen.add(w)
    assert len(seen) > len(words) // 3


def test_window_fillings_are_exact():
    p = make_problem()
    words = set(feasible_brute(p, 8))
    g = FeasibleGraph(p, 8)
    w = sorted(words)[5]
    nodes = g.walk(w)
    fills = _window_fillings(g, nodes, 2, 5)
    assert w[2:5] in fills
    for fl in fills:
        assert (w[:2] + fl + w[5:]) in words
    assert len(fills) == len(set(fills))


def test_optimisers_stay_feasible_and_improve():
    p = make_problem()
    words = set(feasible_brute(p, 8))
    g = FeasibleGraph(p, 8)
    score = lambda w: sum(1 for i in range(len(w) - 1) if w[i] != w[i + 1]) - 3 * w.count("b")
    best_possible = max(score(w) for w in words)
    for fn in (uniform_search, cross_entropy, window_mcmc):
        tr = fn(g, score, 400, seed=1)
        assert tr.best_word in words
        assert tr.evals <= 400
        assert tr.best <= best_possible
        assert all(b1 <= b2 for (_, b1), (_, b2) in zip(tr.curve, tr.curve[1:]))
    # CEM and MCMC should reach the optimum on this small instance
    assert cross_entropy(g, score, 600, seed=2).best == best_possible
    assert window_mcmc(g, score, 600, seed=2).best == best_possible
