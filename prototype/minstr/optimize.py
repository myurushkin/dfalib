"""Optimising an arbitrary (black-box) score over the feasible strings.

Everything here works on a ``FeasibleGraph``: the layered graph of *all*
strings of a given length that satisfy the formula, pruned so that every node
has at least one completion.  That gives three things for free:

* no dead ends: any walk that follows graph edges ends in a feasible string;
* exact path counts: uniform sampling and uniform *local* resampling;
* a compact policy domain: a policy is a table over graph nodes.

Three optimisers over a score ``f(word) -> float`` (higher is better):

* ``uniform_search``       -- sample uniformly, keep the best (the baseline);
* ``cross_entropy``        -- tabular policy over nodes, elite refit each round;
* ``window_mcmc``          -- Metropolis chain whose move resamples a window
                              uniformly among all feasible fillings with the
                              same boundary states (symmetric proposal).

All of them report an *anytime curve*: best score after every k evaluations.
"""

from __future__ import annotations

import math
import random

from .search import all_minimal


class BudgetExhausted(Exception):
    """Raised by Tracker when the evaluation budget is spent."""


class FeasibleGraph:
    """Layered graph of feasible strings of exactly ``length`` symbols."""

    def __init__(self, problem, length):
        graph, _ = all_minimal(problem, length=length)
        if graph is None:
            raise ValueError(f"no feasible string of length {length}")
        self.problem = problem
        self.length = length
        self.root = (0, graph.layers[0][0])
        goals = set((length, s) for s in graph.goals)
        # backward pass: keep only nodes with a completion
        alive = set(goals)
        succs = {}
        for d in range(length, 0, -1):
            for s in graph.layers[d]:
                node = (d, s)
                if node not in alive:
                    continue
                for p, ch in graph.preds[node]:
                    pn = (d - 1, p)
                    alive.add(pn)
                    succs.setdefault(pn, []).append((ch, node))
        for node in succs:
            succs[node].sort()
        self.succs = succs
        self.alive = alive
        # completions[node] = number of feasible suffixes
        comp = {g: 1 for g in goals}
        for d in range(length - 1, -1, -1):
            for node in [n for n in alive if n[0] == d]:
                comp[node] = sum(comp[n] for _, n in succs.get(node, ()))
        self.completions = comp

    def count(self):
        return self.completions[self.root]

    def sample(self, rng):
        node, out = self.root, []
        while node[0] < self.length:
            options = self.succs[node]
            weights = [self.completions[n] for _, n in options]
            ch, node = rng.choices(options, weights=weights)[0]
            out.append(ch)
        return "".join(out)

    def walk(self, word):
        """Nodes visited by a feasible word (length+1 of them)."""
        node, nodes = self.root, [self.root]
        for ch in word:
            nxt = None
            for c, n in self.succs[node]:
                if c == ch:
                    nxt = n
                    break
            if nxt is None:
                raise ValueError(f"{word!r} is not feasible")
            node = nxt
            nodes.append(node)
        return nodes


class Tracker:
    """Records the anytime curve of an optimiser."""

    def __init__(self, score, budget):
        self.score = score
        self.budget = budget
        self.evals = 0
        self.calls = 0                 # including cache hits; caps the loops
        self.best = -math.inf
        self.best_word = None
        self.curve = []                # (evals, best)
        self.cache = {}

    def __call__(self, word):
        self.calls += 1
        if self.exhausted():
            raise BudgetExhausted
        if word in self.cache:
            return self.cache[word]
        v = self.score(word)
        self.cache[word] = v
        self.evals += 1
        if v > self.best:
            self.best, self.best_word = v, word
        self.curve.append((self.evals, self.best))
        return v

    def exhausted(self):
        return self.evals >= self.budget or self.calls >= 20 * self.budget


# ---------------------------------------------------------------------------

def uniform_search(graph, score, budget, seed=0):
    rng = random.Random(seed)
    tr = Tracker(score, budget)
    try:
        while not tr.exhausted():
            tr(graph.sample(rng))
    except BudgetExhausted:
        pass
    return tr


def cross_entropy(graph, score, budget, seed=0, batch=64, elite_frac=0.15, smooth=0.7):
    """Tabular CEM: p[node][symbol], initialised to the uniform-over-strings
    policy (path-count proportional), refit on the elite each round."""
    rng = random.Random(seed)
    tr = Tracker(score, budget)
    table = {}

    def probs(node):
        if node not in table:
            opts = graph.succs[node]
            tot = sum(graph.completions[n] for _, n in opts)
            table[node] = {ch: graph.completions[n] / tot for ch, n in opts}
        return table[node]

    def sample():
        node, out = graph.root, []
        while node[0] < graph.length:
            p = probs(node)
            chs = list(p)
            ch = rng.choices(chs, weights=[p[c] for c in chs])[0]
            out.append(ch)
            node = next(n for c, n in graph.succs[node] if c == ch)
        return "".join(out)

    try:
        while not tr.exhausted():
            words = [sample() for _ in range(batch)]
            scored = sorted(((tr(w), w) for w in words), reverse=True)
            n_elite = max(2, int(len(scored) * elite_frac))
            counts = {}
            for _, w in scored[:n_elite]:
                nodes = graph.walk(w)
                for node, ch in zip(nodes, w):
                    counts.setdefault(node, {}).setdefault(ch, 0)
                    counts[node][ch] += 1
            for node, cnt in counts.items():
                p = probs(node)
                tot = sum(cnt.values())
                for ch in p:
                    target = cnt.get(ch, 0) / tot
                    p[ch] = smooth * target + (1 - smooth) * p[ch]
                # keep every feasible symbol reachable
                floor = 0.02 / len(p)
                for ch in p:
                    p[ch] = max(p[ch], floor)
                z = sum(p.values())
                for ch in p:
                    p[ch] /= z
    except BudgetExhausted:
        pass
    return tr


def _window_fillings(graph, nodes, i, j):
    """All fillings of word[i:j] that lead from nodes[i] to nodes[j]."""
    start, end = nodes[i], nodes[j]
    layer = {start: [""]}
    for _ in range(j - i):
        nxt = {}
        for node, prefixes in layer.items():
            for ch, n in graph.succs[node]:
                nxt.setdefault(n, []).extend(p + ch for p in prefixes)
        layer = nxt
    return layer.get(end, [])


def window_mcmc(graph, score, budget, seed=0, window=4, temperature=1.0, restarts=0):
    """Metropolis chain over feasible strings.  The proposal resamples a random
    window uniformly among all fillings with the same boundary states, which
    is symmetric, so the acceptance ratio is just exp((f' - f) / T)."""
    rng = random.Random(seed)
    tr = Tracker(score, budget)
    L = graph.length
    try:
        cur = graph.sample(rng)
        fcur = tr(cur)
        while not tr.exhausted():
            w = rng.randint(1, min(window, L))
            i = rng.randint(0, L - w)
            j = i + w
            nodes = graph.walk(cur)
            fills = _window_fillings(graph, nodes, i, j)
            if len(fills) <= 1:
                continue
            new = cur[:i] + rng.choice(fills) + cur[j:]
            fnew = tr(new)
            if new == cur:
                continue
            if fnew >= fcur or rng.random() < math.exp((fnew - fcur) / temperature):
                cur, fcur = new, fnew
    except BudgetExhausted:
        pass
    return tr
