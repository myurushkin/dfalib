"""Lazy search for minimal strings satisfying a Boolean formula over trackers.

The product automaton is never built.  A search state is

    (residual formula, ((leaf i, tracker state), ...))

restricted to the leaves that still occur in the residual formula.  Moving by
one symbol steps every live tracker; leaves whose future became decided are
folded into the formula as constants and dropped.

``find_minimal``  -- A* with the admissible bound derived from the trackers
                     (max over conjuncts, min over disjuncts); with unit costs
                     and a consistent integer bound this is a bucket queue.
``all_minimal``   -- the layered graph of *all* optimal-length solutions:
                     exact count, enumeration, uniform sampling.
"""

from __future__ import annotations

import random
import time
from collections import deque

from . import formula as F
from .nfa import INF


class Problem:
    def __init__(self, trackers, formula, alphabet, min_len=0, max_len=None, fold=True):
        self.trackers = list(trackers)
        self.formula = formula
        self.alphabet = tuple(alphabet)
        self.min_len = min_len
        self.max_len = max_len if max_len is not None else INF
        # fold=False disables the on-the-fly formula simplification, so decided
        # leaves stay in the tuple.  Only used to measure what folding buys.
        self.fold = fold

    # ---- state handling ------------------------------------------------
    # A state is (residual formula, live leaf states, phase) where phase is the
    # length read so far capped at min_len: below min_len the same tracker
    # configuration is *not* the same search state, because it cannot be a goal.
    def initial(self):
        states = {i: t.start for i, t in enumerate(self.trackers)}
        return self._canon(self.formula, states, 0)

    def _canon(self, f, states, phase):
        """Fold decided leaves into the formula, keep only the live ones."""
        known = {}
        for i in (F.leaves(f) if self.fold else ()):
            t = self.trackers[i]
            s = states[i]
            if t.always(s):
                known[i] = True
            elif t.min_remaining(s) == INF:
                known[i] = False
        if known:
            f = F.substitute(f, known)
        live = F.leaves(f)
        return (f, tuple((i, states[i]) for i in live), min(phase, self.min_len))

    def successors(self, state):
        f, live, phase = state
        for ch in self.alphabet:
            nxt = {i: self.trackers[i].step(s, ch) for i, s in live}
            yield ch, self._canon(f, nxt, phase + 1)

    def is_goal(self, state, length):
        if length < self.min_len:
            return False
        f, live, _ = state
        if f == F.TRUE:
            return True
        if f == F.FALSE:
            return False
        bits = {i: self.trackers[i].accepts(s) for i, s in live}
        return F.eval_now(f, bits)

    def bound(self, state):
        f, live, phase = state
        if f == F.FALSE:
            return INF
        rem = {i: self.trackers[i].min_remaining(s) for i, s in live}
        b = F.lower_bound(f, rem)
        need = self.min_len - phase
        return b if b >= need else need


class Stats:
    def __init__(self):
        self.expanded = 0
        self.generated = 0
        self.distinct = 0
        self.seconds = 0.0

    def as_dict(self):
        return dict(expanded=self.expanded, generated=self.generated,
                    distinct=self.distinct, seconds=round(self.seconds, 4))


def find_minimal(problem, stats=None):
    """Return (string, stats) for one minimal solution, or (None, stats).

    A* over the lazy product with a bucket queue keyed by g+h.  Nodes are
    closed when *expanded*; a node generated again with a smaller g is
    re-pushed and the stale queue entry is skipped when it surfaces.
    """
    stats = stats or Stats()
    t0 = time.perf_counter()
    start = problem.initial()
    h0 = problem.bound(start)
    if h0 == INF or h0 > problem.max_len:
        stats.seconds = time.perf_counter() - t0
        return None, stats
    parent = {start: None}
    g_of = {start: 0}
    closed = set()
    buckets = {}

    def push(state, g, h):
        buckets.setdefault(g + h, deque()).append((state, g))

    push(start, 0, h0)
    fcur = h0
    while buckets:
        while fcur not in buckets or not buckets[fcur]:
            buckets.pop(fcur, None)
            if not buckets:
                stats.seconds = time.perf_counter() - t0
                stats.distinct = len(g_of)
                return None, stats
            fcur = min(buckets)
        state, g = buckets[fcur].popleft()
        if state in closed or g != g_of[state]:
            continue                                    # stale entry
        if problem.is_goal(state, g):
            stats.seconds = time.perf_counter() - t0
            stats.distinct = len(g_of)
            return _reconstruct(parent, state), stats
        closed.add(state)
        stats.expanded += 1
        if g + 1 > problem.max_len:
            continue
        for ch, nxt in problem.successors(state):
            stats.generated += 1
            g2 = g + 1
            old = g_of.get(nxt)
            if old is not None and old <= g2:
                continue
            h = problem.bound(nxt)
            if h == INF or g2 + h > problem.max_len:
                continue
            g_of[nxt] = g2
            parent[nxt] = (state, ch)
            push(nxt, g2, h)
    stats.seconds = time.perf_counter() - t0
    stats.distinct = len(g_of)
    return None, stats


def _reconstruct(parent, state):
    out = []
    while parent[state] is not None:
        state, ch = parent[state]
        out.append(ch)
    return "".join(reversed(out))


class SolutionGraph:
    """Layered graph of every optimal-length solution.

    Nodes are (depth, state).  ``count()`` and ``sample()`` use path counts,
    ``enumerate()`` yields strings without repetition.
    """

    def __init__(self, problem, length, layers, preds, goals):
        self.problem = problem
        self.length = length
        self.layers = layers          # depth -> list of states
        self.preds = preds            # (depth, state) -> list of (prev_state, ch)
        self.goals = goals            # list of states at depth == length
        self._paths = None

    def nodes(self):
        return sum(len(l) for l in self.layers)

    def _path_counts(self):
        """Number of paths from the root to every node (forward DP)."""
        if self._paths is not None:
            return self._paths
        cnt = {(0, self.layers[0][0]): 1}
        for d in range(1, self.length + 1):
            for s in self.layers[d]:
                cnt[(d, s)] = sum(cnt[(d - 1, p)] for p, _ in self.preds[(d, s)])
        self._paths = cnt
        return cnt

    def count(self):
        cnt = self._path_counts()
        return sum(cnt[(self.length, s)] for s in self.goals)

    def enumerate(self, limit=None):
        n = 0
        for goal in self.goals:
            stack = [(self.length, goal, [])]
            while stack:
                d, s, suffix = stack.pop()
                if d == 0:
                    yield "".join(reversed(suffix))
                    n += 1
                    if limit is not None and n >= limit:
                        return
                    continue
                for p, ch in self.preds[(d, s)]:
                    stack.append((d - 1, p, suffix + [ch]))

    def sample(self, rng=None):
        """One uniformly random optimal-length solution."""
        rng = rng or random
        cnt = self._path_counts()
        weights = [cnt[(self.length, s)] for s in self.goals]
        s = rng.choices(self.goals, weights=weights)[0]
        out = []
        d = self.length
        while d > 0:
            preds = self.preds[(d, s)]
            w = [cnt[(d - 1, p)] for p, _ in preds]
            p, ch = rng.choices(preds, weights=w)[0]
            out.append(ch)
            s, d = p, d - 1
        return "".join(reversed(out))


def all_minimal(problem, length=None, stats=None):
    """Build the solution graph for the optimal length (or a given one)."""
    stats = stats or Stats()
    if length is None:
        first, stats = find_minimal(problem, stats)
        if first is None:
            return None, stats
        length = len(first)
    t0 = time.perf_counter()
    start = problem.initial()
    layers = [[start]]
    preds = {}
    seen = {start}
    frontier = [start]
    for d in range(1, length + 1):
        nxt_layer = []
        nxt_seen = {}
        for s in frontier:
            for ch, t in problem.successors(s):
                h = problem.bound(t)
                if h == INF or d + h > length:
                    continue
                stats.generated += 1
                if t not in nxt_seen:
                    nxt_seen[t] = []
                    nxt_layer.append(t)
                nxt_seen[t].append((s, ch))
            stats.expanded += 1
        for t, plist in nxt_seen.items():
            preds[(d, t)] = plist
        layers.append(nxt_layer)
        frontier = nxt_layer
    goals = [s for s in frontier if problem.is_goal(s, length)]
    stats.seconds += time.perf_counter() - t0
    stats.distinct = sum(len(l) for l in layers)
    if not goals:
        return None, stats
    return SolutionGraph(problem, length, layers, preds, goals), stats
