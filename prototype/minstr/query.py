"""Tiny text format for problems.

    alphabet: abcd
    length: 0..30            # optional; also "length: <= 30"
    A = .*aa.*               # regex (may reference earlier names as <A>)
    B = count("cc") >= 3
    C = runs(a, 2) >= 2
    D = balanced(a, ., c, 1, 3)
    query: A and (B or not C) and D

Boolean precedence: not > and > or; parentheses allowed.
"""

from __future__ import annotations

import re

from . import formula as F
from .nfa import parse_regex
from .search import Problem
from .trackers import RegexTracker, CountTracker, RunsTracker, BalancedTracker


class QueryError(ValueError):
    pass


_COUNT = re.compile(r'^count\(\s*"([^"]+)"\s*\)\s*>=\s*(\d+)\s*$')
_RUNS = re.compile(r'^runs\(\s*(\S)\s*,\s*(\d+)\s*\)\s*>=\s*(\d+)\s*$')
_BAL = re.compile(r'^balanced\(\s*(\S)\s*,\s*(.+?)\s*,\s*(\S)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)\s*$')


def parse_problem(text):
    alphabet = None
    min_len, max_len = 0, None
    names = []
    trackers = []
    macros = {}
    query = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("alphabet:"):
            alphabet = line[len("alphabet:"):].strip()
            continue
        if line.startswith("length:"):
            spec = line[len("length:"):].strip()
            if spec.startswith("<="):
                max_len = int(spec[2:])
            elif ".." in spec:
                lo, hi = spec.split("..")
                min_len, max_len = int(lo), int(hi)
            else:
                min_len = max_len = int(spec)
            continue
        if line.startswith("query:"):
            query = line[len("query:"):].strip()
            continue
        if "=" not in line:
            raise QueryError(f"cannot parse line: {raw!r}")
        if alphabet is None:
            raise QueryError("alphabet must be declared before definitions")
        name, rhs = (s.strip() for s in line.split("=", 1))
        if not re.match(r"^[A-Za-z_]\w*$", name):
            raise QueryError(f"bad name {name!r}")
        m = _COUNT.match(rhs)
        if m:
            trackers.append(CountTracker(m.group(1), int(m.group(2)), alphabet, name=name))
        elif (m := _RUNS.match(rhs)):
            trackers.append(RunsTracker(m.group(1), int(m.group(2)), int(m.group(3)), alphabet, name=name))
        elif (m := _BAL.match(rhs)):
            trackers.append(BalancedTracker(m.group(1), m.group(2), m.group(3),
                                            int(m.group(4)), int(m.group(5)), alphabet,
                                            macros=macros, name=name))
        else:
            trackers.append(RegexTracker(rhs, alphabet, macros=macros, name=name))
            macros[name] = parse_regex(rhs, alphabet, macros)
        names.append(name)
    if alphabet is None or query is None:
        raise QueryError("need both 'alphabet:' and 'query:'")
    f = _parse_bool(query, {n: i for i, n in enumerate(names)})
    return Problem(trackers, f, alphabet, min_len, max_len), names


_TOK = re.compile(r"\s*(\(|\)|and|or|not|[A-Za-z_]\w*)\s*")


def _parse_bool(text, index):
    tokens = []
    pos = 0
    while pos < len(text):
        m = _TOK.match(text, pos)
        if not m or m.end() == pos:
            raise QueryError(f"bad query near {text[pos:]!r}")
        tokens.append(m.group(1))
        pos = m.end()
    tokens.append("$")
    i = 0

    def peek():
        return tokens[i]

    def take():
        nonlocal i
        i += 1
        return tokens[i - 1]

    def p_or():
        parts = [p_and()]
        while peek() == "or":
            take()
            parts.append(p_and())
        return F.OR(*parts)

    def p_and():
        parts = [p_not()]
        while peek() == "and":
            take()
            parts.append(p_not())
        return F.AND(*parts)

    def p_not():
        if peek() == "not":
            take()
            return F.NOT(p_not())
        return p_atom()

    def p_atom():
        t = take()
        if t == "(":
            f = p_or()
            if take() != ")":
                raise QueryError("missing ')'")
            return f
        if t not in index:
            raise QueryError(f"unknown name {t!r}")
        return F.leaf(index[t])

    f = p_or()
    if peek() != "$":
        raise QueryError(f"trailing tokens in query: {tokens[i:-1]}")
    return f
