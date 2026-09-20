"""Eager baseline: determinise every leaf, fold the formula into one explicit
product DFA (minimising after every operation), then BFS.

This mirrors the conventional pipeline and exists only to be measured against
the lazy search.  Trackers other than plain regexes are first expanded into
equivalent regular expressions via ``to_regex()``.
"""

from __future__ import annotations

import time
from collections import deque

from .nfa import NFA
from . import formula as F


class TooLarge(RuntimeError):
    pass


class DFA:
    """Complete DFA: ``trans[q][a]`` with ``a`` an alphabet index."""

    def __init__(self, alphabet, trans, accepting, start=0):
        self.alphabet = tuple(alphabet)
        self.trans = trans
        self.accepting = set(accepting)
        self.start = start

    @property
    def n(self):
        return len(self.trans)

    @classmethod
    def from_nfa(cls, nfa, limit):
        alpha = nfa.alphabet
        index = {nfa.start_mask: 0}
        order = [nfa.start_mask]
        trans = []
        i = 0
        while i < len(order):
            mask = order[i]
            row = []
            for ch in alpha:
                nxt = nfa.step(mask, ch)
                if nxt not in index:
                    index[nxt] = len(order)
                    order.append(nxt)
                    if len(order) > limit:
                        raise TooLarge(f"determinisation exceeded {limit} states")
                row.append(index[nxt])
            trans.append(row)
            i += 1
        acc = {index[m] for m in order if nfa.accepts(m)}
        return cls(alpha, trans, acc)

    def complement(self):
        return DFA(self.alphabet, [list(r) for r in self.trans],
                   set(range(self.n)) - self.accepting, self.start)

    def product(self, other, op, limit):
        """Reachable product; ``op`` in {"A", "O"}."""
        index = {(self.start, other.start): 0}
        order = [(self.start, other.start)]
        trans = []
        i = 0
        k = len(self.alphabet)
        while i < len(order):
            p, q = order[i]
            row = []
            for a in range(k):
                pair = (self.trans[p][a], other.trans[q][a])
                if pair not in index:
                    index[pair] = len(order)
                    order.append(pair)
                    if len(order) > limit:
                        raise TooLarge(f"product exceeded {limit} states")
                row.append(index[pair])
            trans.append(row)
            i += 1
        if op == "A":
            acc = {index[pq] for pq in order if pq[0] in self.accepting and pq[1] in other.accepting}
        else:
            acc = {index[pq] for pq in order if pq[0] in self.accepting or pq[1] in other.accepting}
        return DFA(self.alphabet, trans, acc)

    def minimize(self):
        """Moore partition refinement."""
        n = self.n
        k = len(self.alphabet)
        block = [1 if q in self.accepting else 0 for q in range(n)]
        nblocks = 2
        while True:
            sig = {}
            new = [0] * n
            for q in range(n):
                key = (block[q],) + tuple(block[self.trans[q][a]] for a in range(k))
                if key not in sig:
                    sig[key] = len(sig)
                new[q] = sig[key]
            if len(sig) == nblocks:
                break
            block, nblocks = new, len(sig)
        rep = {}
        for q in range(n):
            rep.setdefault(block[q], q)
        trans = [[block[self.trans[rep[b]][a]] for a in range(k)] for b in range(nblocks)]
        acc = {block[q] for q in self.accepting}
        return DFA(self.alphabet, trans, acc, block[self.start])

    def shortest(self, min_len=0, max_len=None):
        # BFS over (state, depth) keys.  Depths are only distinguished below
        # ``min_len`` (beyond it behaviour depends on the state alone), so the
        # search stays O(states * min_len) and, unlike plain state-BFS, does
        # not miss an accepting state whose first visit happens too early.
        key0 = (self.start, 0)
        parent = {key0: None}
        dq = deque([(self.start, 0)])
        while dq:
            q, d = dq.popleft()
            key = (q, min(d, min_len))
            if q in self.accepting and d >= min_len:
                out = []
                while parent[key] is not None:
                    key, a = parent[key]
                    out.append(self.alphabet[a])
                return "".join(reversed(out))
            if max_len is not None and d >= max_len:
                continue
            for a, t in enumerate(self.trans[q]):
                tkey = (t, min(d + 1, min_len))
                if tkey not in parent:
                    parent[tkey] = (key, a)
                    dq.append((t, d + 1))
        return None

    def count_shortest(self, length):
        """Number of accepted words of exactly ``length`` (layered DP)."""
        cur = {self.start: 1}
        for _ in range(length):
            nxt = {}
            for q, c in cur.items():
                for t in self.trans[q]:
                    nxt[t] = nxt.get(t, 0) + c
            cur = nxt
        return sum(c for q, c in cur.items() if q in self.accepting)


class EagerStats:
    def __init__(self):
        self.peak_states = 0
        self.final_states = 0
        self.seconds_build = 0.0
        self.seconds_search = 0.0
        self.failed = None

    def as_dict(self):
        return dict(peak_states=self.peak_states, final_states=self.final_states,
                    seconds_build=round(self.seconds_build, 4),
                    seconds_search=round(self.seconds_search, 4), failed=self.failed)


def build_product(trackers, formula, alphabet, limit=2_000_000, minimize=True, stats=None):
    stats = stats or EagerStats()
    t0 = time.perf_counter()
    leaf_dfa = {}

    def dfa_of(f):
        k = f[0]
        if k == "T":
            d = DFA(alphabet, [[0] * len(alphabet)], {0})
        elif k == "F":
            d = DFA(alphabet, [[0] * len(alphabet)], set())
        elif k == "L":
            i = f[1]
            if i not in leaf_dfa:
                nfa = NFA(trackers[i].to_regex(), alphabet)
                d = DFA.from_nfa(nfa, limit)
                leaf_dfa[i] = d.minimize() if minimize else d
            d = leaf_dfa[i]
        elif k == "N":
            d = dfa_of(f[1]).complement()
        else:
            d = dfa_of(f[1][0])
            for c in f[1][1:]:
                d = d.product(dfa_of(c), k, limit)
                stats.peak_states = max(stats.peak_states, d.n)
                if minimize:
                    d = d.minimize()
        stats.peak_states = max(stats.peak_states, d.n)
        return d

    try:
        dfa = dfa_of(formula)
    except TooLarge as e:
        stats.failed = str(e)
        stats.seconds_build = time.perf_counter() - t0
        return None, stats
    stats.seconds_build = time.perf_counter() - t0
    stats.final_states = dfa.n
    return dfa, stats


def find_minimal_eager(trackers, formula, alphabet, min_len=0, max_len=None,
                       limit=2_000_000, minimize=True):
    dfa, stats = build_product(trackers, formula, alphabet, limit, minimize)
    if dfa is None:
        return None, stats
    t0 = time.perf_counter()
    s = dfa.shortest(min_len, max_len)
    stats.seconds_search = time.perf_counter() - t0
    return s, stats
