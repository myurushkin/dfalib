"""Disjunctive decomposition must agree with the monolithic lazy search."""

import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from minstr.trackers import RegexTracker, CountTracker
from minstr import formula as F
from minstr.search import Problem, find_minimal
from minstr.decompose import solve_dnf, DecompositionTooLarge

ALPHA = "ab"


def random_formula(rng, n_leaves, depth=0):
    r = rng.random()
    if depth >= 2 or r < 0.35:
        leaf = F.leaf(rng.randrange(n_leaves))
        return F.NOT(leaf) if rng.random() < 0.25 else leaf
    parts = [random_formula(rng, n_leaves, depth + 1)
             for _ in range(rng.randint(2, 3))]
    return F.AND(*parts) if r < 0.7 else F.OR(*parts)


def random_trackers(rng, n):
    out = []
    for i in range(n):
        if rng.random() < 0.3:
            out.append(CountTracker(rng.choice(["a", "b", "ab", "ba"]),
                                    rng.randint(1, 2), ALPHA, name=f"C{i}"))
        else:
            pats = [".*aa.*", ".*ab.*", ".*b.b.*", "a.*", ".*bb", "(ab)*",
                    ".*aba.*", "b+a*"]
            out.append(RegexTracker(rng.choice(pats), ALPHA, name=f"R{i}"))
    return out


def test_matches_monolithic_on_random_queries():
    rng = random.Random(7)
    for trial in range(120):
        trackers = random_trackers(rng, rng.randint(2, 4))
        formula = random_formula(rng, len(trackers))
        mono, _ = find_minimal(Problem(trackers, formula, ALPHA, max_len=10))
        deco, st = solve_dnf(trackers, formula, ALPHA, max_len=10)
        assert (mono is None) == (deco is None), (trial, formula, mono, deco)
        if mono is not None:
            assert len(mono) == len(deco), (trial, formula, mono, deco)


def test_fixed_length_feasibility_matches():
    rng = random.Random(11)
    for trial in range(60):
        trackers = random_trackers(rng, rng.randint(2, 4))
        formula = random_formula(rng, len(trackers))
        for L in (4, 6):
            mono, _ = find_minimal(
                Problem(trackers, formula, ALPHA, min_len=L, max_len=L))
            deco, st = solve_dnf(trackers, formula, ALPHA,
                                 min_len=L, max_len=L, stop_at_first=True)
            assert (mono is None) == (deco is None), (trial, L, formula)
            if deco is not None:
                assert len(deco) == L


def test_union_prunes_after_matching_bound():
    # 50 disjuncts with identical structure: the sorted sweep must stop as
    # soon as one conjunct achieves its own lower bound.
    trackers = [RegexTracker(f".*a{{{3}}}b{{{i % 3 + 1}}}.*", ALPHA, name=f"U{i}")
                for i in range(50)]
    formula = F.OR(*[F.leaf(i) for i in range(len(trackers))])
    word, st = solve_dnf(trackers, formula, ALPHA, max_len=12)
    assert word is not None and len(word) == 4
    assert st.solved < st.conjuncts  # the tail was pruned, not searched


def test_conjunct_cap():
    trackers = random_trackers(random.Random(3), 24)
    # AND of 12 two-way ORs over disjoint leaves -> 2^12 conjuncts.
    formula = F.AND(*[F.OR(F.leaf(2 * i), F.leaf(2 * i + 1)) for i in range(12)])
    try:
        solve_dnf(trackers, formula, ALPHA, max_len=6, max_conjuncts=100)
        assert False, "expected DecompositionTooLarge"
    except DecompositionTooLarge:
        pass
