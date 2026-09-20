"""Boolean formulas over tracker leaves, with on-the-fly simplification.

A formula is an interned tuple:

    ("T",)                 constant true
    ("F",)                 constant false
    ("L", i)               leaf i (the i-th tracker)
    ("N", child)           negation
    ("A", (c1, c2, ...))   conjunction  (flattened, sorted, deduplicated)
    ("O", (c1, c2, ...))   disjunction  (flattened, sorted, deduplicated)

The search keeps, per state, the *residual* formula: leaves whose future is
already decided (accepted for ever, or dead) have been substituted by constants
and dropped from the state.  That is what lets tuples shrink while searching.
"""

from __future__ import annotations

from .nfa import INF

TRUE = ("T",)
FALSE = ("F",)


def leaf(i):
    return ("L", i)


def NOT(f):
    if f == TRUE:
        return FALSE
    if f == FALSE:
        return TRUE
    if f[0] == "N":
        return f[1]
    return ("N", f)


def _nary(kind, parts):
    ident, absorb = (TRUE, FALSE) if kind == "A" else (FALSE, TRUE)
    flat = []
    for p in parts:
        if p == absorb:
            return absorb
        if p == ident:
            continue
        if p[0] == kind:
            flat.extend(p[1])
        else:
            flat.append(p)
    flat = sorted(set(flat), key=repr)
    if not flat:
        return ident
    if len(flat) == 1:
        return flat[0]
    # x and not x  /  x or not x
    s = set(flat)
    for p in flat:
        if p[0] == "N" and p[1] in s:
            return absorb
    return (kind, tuple(flat))


def AND(*parts):
    return _nary("A", parts)


def OR(*parts):
    return _nary("O", parts)


def leaves(f):
    """Sorted tuple of leaf indices occurring in f."""
    out = set()
    stack = [f]
    while stack:
        g = stack.pop()
        k = g[0]
        if k == "L":
            out.add(g[1])
        elif k == "N":
            stack.append(g[1])
        elif k in "AO":
            stack.extend(g[1])
    return tuple(sorted(out))


def eval_now(f, bits):
    """Evaluate with ``bits[i]`` = does leaf i accept the string read so far."""
    k = f[0]
    if k == "T":
        return True
    if k == "F":
        return False
    if k == "L":
        return bits[f[1]]
    if k == "N":
        return not eval_now(f[1], bits)
    if k == "A":
        return all(eval_now(c, bits) for c in f[1])
    return any(eval_now(c, bits) for c in f[1])


def substitute(f, known):
    """Replace leaves listed in ``known`` (i -> True/False) by constants and fold."""
    k = f[0]
    if k in "TF":
        return f
    if k == "L":
        v = known.get(f[1])
        if v is None:
            return f
        return TRUE if v else FALSE
    if k == "N":
        return NOT(substitute(f[1], known))
    if k == "A":
        return AND(*(substitute(c, known) for c in f[1]))
    return OR(*(substitute(c, known) for c in f[1]))


def lower_bound(f, remaining):
    """Admissible bound on the symbols still needed to make f true.

    ``remaining[i]`` is the tracker's own lower bound for leaf i.  Negated
    leaves contribute 0 (we know nothing cheap about *not* accepting).
    """
    k = f[0]
    if k == "T":
        return 0
    if k == "F":
        return INF
    if k == "L":
        return remaining[f[1]]
    if k == "N":
        return 0
    if k == "A":
        best = 0
        for c in f[1]:
            v = lower_bound(c, remaining)
            if v > best:
                best = v
        return best
    best = INF
    for c in f[1]:
        v = lower_bound(c, remaining)
        if v < best:
            best = v
    return best


def to_dnf(f):
    """List of conjunctions (each a list of literals: ("L",i) or ("N",("L",i)))."""
    k = f[0]
    if k == "T":
        return [[]]
    if k == "F":
        return []
    if k == "L":
        return [[f]]
    if k == "N":
        inner = f[1]
        if inner[0] == "L":
            return [[f]]
        if inner[0] == "A":
            return to_dnf(OR(*(NOT(c) for c in inner[1])))
        if inner[0] == "O":
            return to_dnf(AND(*(NOT(c) for c in inner[1])))
        return to_dnf(inner[1])          # double negation
    if k == "O":
        out = []
        for c in f[1]:
            out.extend(to_dnf(c))
        return out
    # conjunction: cartesian product of children's DNFs
    result = [[]]
    for c in f[1]:
        cd = to_dnf(c)
        result = [a + b for a in result for b in cd]
    return result


def pretty(f, names):
    k = f[0]
    if k == "T":
        return "true"
    if k == "F":
        return "false"
    if k == "L":
        return names[f[1]]
    if k == "N":
        return "not " + _paren(f[1], names)
    op = " and " if k == "A" else " or "
    return op.join(_paren(c, names) for c in f[1])


def _paren(f, names):
    s = pretty(f, names)
    return f"({s})" if f[0] in "AO" else s
