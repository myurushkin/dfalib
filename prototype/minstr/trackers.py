"""Trackers: small deterministic machines that read a string symbol by symbol.

A tracker exposes exactly what the lazy search needs:

* ``start``                 -- initial state (hashable);
* ``step(state, symbol)``   -- next state;
* ``accepts(state)``        -- is the constraint satisfied *by the string read so far*;
* ``always(state)``         -- satisfied now and for every continuation (absorbing);
* ``min_remaining(state)``  -- admissible lower bound on the number of further
                               symbols needed before the constraint can be
                               satisfied (INF if it never can);
* ``to_regex()``            -- an equivalent regular expression, used only by the
                               eager-product baseline for apples-to-apples runs.

Every tracker is domain-neutral: it is a machine over an arbitrary finite
alphabet.  Trackers for thresholded counting functions are what makes
"count >= k" style constraints cheap: the counter saturates at k, so the state
space grows by a factor of k+1 instead of being unbounded.
"""

from __future__ import annotations

from .nfa import NFA, INF


class Tracker:
    name = "tracker"

    def __init__(self, alphabet):
        self.alphabet = tuple(alphabet)

    def step(self, state, ch):
        raise NotImplementedError

    def accepts(self, state):
        raise NotImplementedError

    def always(self, state):
        return False

    def min_remaining(self, state):
        return 0

    def to_regex(self):
        raise NotImplementedError

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"


# --------------------------------------------------------------------------

class RegexTracker(Tracker):
    """Membership in a regular language, carried as a subset of NFA states."""

    def __init__(self, pattern, alphabet, macros=None, name=None):
        super().__init__(alphabet)
        self.nfa = NFA(pattern, alphabet, macros)
        self.pattern = pattern
        self.name = name or pattern
        self.start = self.nfa.start_mask

    def step(self, state, ch):
        return self.nfa.step(state, ch)

    def accepts(self, state):
        return self.nfa.accepts(state)

    def always(self, state):
        return self.nfa.always(state)

    def min_remaining(self, state):
        return self.nfa.min_remaining(state)

    def to_regex(self):
        return self.pattern


# --------------------------------------------------------------------------

def _kmp_table(sub):
    fail = [0] * len(sub)
    k = 0
    for i in range(1, len(sub)):
        while k and sub[i] != sub[k]:
            k = fail[k - 1]
        if sub[i] == sub[k]:
            k += 1
        fail[i] = k
    return fail


class CountTracker(Tracker):
    """At least ``k`` non-overlapping occurrences of ``sub``.

    State = (length of the current partial match, occurrences seen capped at k).
    Greedy left-to-right non-overlapping counting is exactly what the regular
    expression ``(.*sub){k}.*`` expresses, so the baseline expansion is exact.
    """

    def __init__(self, sub, k, alphabet, name=None):
        super().__init__(alphabet)
        if k < 1 or not sub:
            raise ValueError("CountTracker needs k >= 1 and a non-empty substring")
        self.sub = sub
        self.k = k
        self.fail = _kmp_table(sub)
        self.name = name or f"count({sub})>={k}"
        self.start = (0, 0)

    def step(self, state, ch):
        j, cnt = state
        if cnt >= self.k:
            return state
        while j and self.sub[j] != ch:
            j = self.fail[j - 1]
        if self.sub[j] == ch:
            j += 1
        if j == len(self.sub):
            return (0, min(cnt + 1, self.k))      # reset: non-overlapping
        return (j, cnt)

    def accepts(self, state):
        return state[1] >= self.k

    def always(self, state):
        return state[1] >= self.k

    def min_remaining(self, state):
        j, cnt = state
        need = self.k - cnt
        if need <= 0:
            return 0
        return (len(self.sub) - j) + (need - 1) * len(self.sub)

    def to_regex(self):
        return f"(.*{_lit(self.sub)}){{{self.k}}}.*"


# --------------------------------------------------------------------------

class RunsTracker(Tracker):
    """At least ``k`` maximal runs of symbol ``sym`` of length >= ``m``.

    State = (current run length capped at m, runs counted capped at k).
    """

    def __init__(self, sym, m, k, alphabet, name=None):
        super().__init__(alphabet)
        if m < 1 or k < 1 or sym not in self.alphabet:
            raise ValueError("RunsTracker needs m,k >= 1 and sym in alphabet")
        self.sym, self.m, self.k = sym, m, k
        self.name = name or f"runs({sym},{m})>={k}"
        self.start = (0, 0)

    def step(self, state, ch):
        run, cnt = state
        if cnt >= self.k:
            return state
        if ch == self.sym:
            if run >= self.m:
                return state
            run += 1
            if run == self.m:
                return (run, cnt + 1)
            return (run, cnt)
        return (0, cnt)

    def accepts(self, state):
        return state[1] >= self.k

    def always(self, state):
        return state[1] >= self.k

    def min_remaining(self, state):
        run, cnt = state
        need = self.k - cnt
        if need <= 0:
            return 0
        first = (self.m - run) if run < self.m else (self.m + 1)
        return first + (need - 1) * (self.m + 1)

    def to_regex(self):
        others = "".join(c for c in self.alphabet if c != self.sym)
        if not others:
            raise ValueError("RunsTracker needs at least one other symbol")
        x, m, k = self.sym, self.m, self.k
        sep = f"[{others}]"
        # each of the first k-1 blocks is a run of >= m ending at a run boundary
        # (forced by the separator); the last block may sit anywhere after it.
        block = f".*{x}{{{m}}}{x}*{sep}+"
        return f"({block}){{{k - 1}}}.*{x}{{{m}}}.*" if k > 1 else f".*{x}{{{m}}}.*"


# --------------------------------------------------------------------------

_ACCEPTED = "ACCEPTED"


class BalancedTracker(Tracker):
    """Contains a factor  left^n  <middle>  right^n  with n in [lo, hi].

    This is the "{n}" construct.  Instead of unrolling into a union over n,
    the tracker keeps a small set of threads, each remembering which n it is
    committed to.  State = frozenset of threads, or the absorbing ACCEPTED.

    Threads:
        ("L", c)          -- inside the left block, c symbols matched so far
        ("M", n, mask)    -- inside the middle, committed to n, mask = middle NFA subset
        ("R", n, r)       -- inside the right block, r of n symbols matched
    """

    def __init__(self, left, middle, right, lo, hi, alphabet, macros=None, name=None):
        super().__init__(alphabet)
        if lo < 1 or hi < lo:
            raise ValueError("BalancedTracker needs 1 <= lo <= hi")
        if left not in self.alphabet or right not in self.alphabet:
            raise ValueError("left/right must be single symbols of the alphabet")
        self.left, self.right, self.lo, self.hi = left, right, lo, hi
        self.middle_pattern = middle
        self.mid = NFA(middle, alphabet, macros)
        self.mid_min = self.mid.min_remaining(self.mid.start_mask)
        self.name = name or f"{left}{{n}}({middle}){right}{{n}},n=[{lo}..{hi}]"
        self.start = frozenset()

    def _expand(self, threads):
        out = set(threads)
        for t in threads:
            if t[0] == "L" and t[1] >= self.lo:
                out.add(("M", t[1], self.mid.start_mask))
        for t in list(out):
            if t[0] == "M" and self.mid.accepts(t[2]):
                out.add(("R", t[1], 0))
        return out

    def step(self, state, ch):
        if state == _ACCEPTED:
            return state
        threads = self._expand(state)
        nxt = set()
        if ch == self.left:
            nxt.add(("L", 1))
        for t in threads:
            kind = t[0]
            if kind == "L":
                if ch == self.left and t[1] < self.hi:
                    nxt.add(("L", t[1] + 1))
            elif kind == "M":
                m = self.mid.step(t[2], ch)
                if m:
                    nxt.add(("M", t[1], m))
            else:                                  # "R"
                if ch == self.right:
                    r = t[2] + 1
                    if r == t[1]:
                        return _ACCEPTED
                    nxt.add(("R", t[1], r))
        return frozenset(nxt)

    def accepts(self, state):
        return state == _ACCEPTED

    def always(self, state):
        return state == _ACCEPTED

    def min_remaining(self, state):
        if state == _ACCEPTED:
            return 0
        best = self.lo + self.mid_min + self.lo           # start a fresh match
        for t in self._expand(state):
            kind = t[0]
            if kind == "L":
                n = max(t[1], self.lo)
                cost = (n - t[1]) + self.mid_min + n
            elif kind == "M":
                cost = self.mid.min_remaining(t[2]) + t[1]
            else:
                cost = t[1] - t[2]
            if cost < best:
                best = cost
        return best

    def to_regex(self):
        alts = []
        for n in range(self.lo, self.hi + 1):
            alts.append(f"{self.left}{{{n}}}({self.middle_pattern}){self.right}{{{n}}}")
        return ".*(" + "|".join(alts) + ").*"


def _lit(s):
    """Escape a literal for the regex parser (only meta characters need care)."""
    out = []
    for c in s:
        if c in "()[]|*+?{}.<>":
            raise ValueError(f"literal symbol {c!r} clashes with regex syntax")
        out.append(c)
    return "".join(out)
