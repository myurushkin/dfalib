"""Regular expressions -> Thompson NFA with bitmask subsets.

The NFA is the *leaf* level of the system: every regular constraint of a query
becomes one NFA.  The search never determinises it eagerly; it carries a subset
of NFA states (a bitmask) and steps it symbol by symbol.

Three services are exported for the search:

* ``step(mask, symbol)``  -- move a subset one symbol forward;
* ``min_remaining(mask)`` -- admissible lower bound on how many more symbols are
  needed before this constraint can accept;
* ``always(mask)``        -- True when the constraint accepts now and will keep
  accepting for every continuation (used to drop the leaf from the state).
"""

from __future__ import annotations

INF = float("inf")


class ParseError(ValueError):
    pass


# --------------------------------------------------------------------------
# regex AST
# --------------------------------------------------------------------------

class Node:
    __slots__ = ()


class Sym(Node):
    __slots__ = ("chars",)

    def __init__(self, chars):
        self.chars = frozenset(chars)


class Eps(Node):
    __slots__ = ()


class Cat(Node):
    __slots__ = ("parts",)

    def __init__(self, parts):
        self.parts = list(parts)


class Alt(Node):
    __slots__ = ("parts",)

    def __init__(self, parts):
        self.parts = list(parts)


class Star(Node):
    __slots__ = ("body",)

    def __init__(self, body):
        self.body = body


# --------------------------------------------------------------------------
# parser:  literals, '.', [class], (), |, *, +, ?, {m}, {m,n}
# --------------------------------------------------------------------------

class _Parser:
    def __init__(self, text, alphabet, macros):
        self.s = text
        self.i = 0
        self.alphabet = alphabet
        self.macros = macros or {}

    def peek(self):
        return self.s[self.i] if self.i < len(self.s) else ""

    def eat(self, ch):
        if self.peek() != ch:
            raise ParseError(f"expected {ch!r} at {self.i} in {self.s!r}")
        self.i += 1

    def skip_ws(self):
        while self.i < len(self.s) and self.s[self.i] in " \t\n":
            self.i += 1

    def parse(self):
        node = self.alt()
        self.skip_ws()
        if self.i != len(self.s):
            raise ParseError(f"trailing input at {self.i} in {self.s!r}")
        return node

    def alt(self):
        parts = [self.cat()]
        while True:
            self.skip_ws()
            if self.peek() == "|":
                self.eat("|")
                parts.append(self.cat())
            else:
                break
        return parts[0] if len(parts) == 1 else Alt(parts)

    def cat(self):
        parts = []
        while True:
            self.skip_ws()
            c = self.peek()
            if c == "" or c in "|)":
                break
            parts.append(self.repeat())
        if not parts:
            return Eps()
        return parts[0] if len(parts) == 1 else Cat(parts)

    def repeat(self):
        node = self.atom()
        while True:
            self.skip_ws()
            c = self.peek()
            if c == "*":
                self.eat("*")
                node = Star(node)
            elif c == "+":
                self.eat("+")
                node = Cat([node, Star(node)])
            elif c == "?":
                self.eat("?")
                node = Alt([node, Eps()])
            elif c == "{":
                node = self.bounded(node)
            else:
                return node

    def bounded(self, node):
        self.eat("{")
        digits = ""
        while self.peek().isdigit():
            digits += self.s[self.i]
            self.i += 1
        if not digits:
            raise ParseError(f"bad repetition at {self.i} in {self.s!r}")
        low = int(digits)
        high = low
        if self.peek() == ",":
            self.eat(",")
            digits = ""
            while self.peek().isdigit():
                digits += self.s[self.i]
                self.i += 1
            if not digits:
                raise ParseError(f"open repetition unsupported in {self.s!r}")
            high = int(digits)
        self.eat("}")
        if high < low:
            raise ParseError(f"bad repetition range in {self.s!r}")
        parts = [node] * low
        for _ in range(high - low):
            parts.append(Alt([node, Eps()]))
        if not parts:
            return Eps()
        return Cat(parts)

    def atom(self):
        self.skip_ws()
        c = self.peek()
        if c == "(":
            self.eat("(")
            node = self.alt()
            self.skip_ws()
            self.eat(")")
            return node
        if c == "[":
            return self.charclass()
        if c == ".":
            self.eat(".")
            return Sym(self.alphabet)
        if c == "<":                      # <name> expands a named macro
            self.eat("<")
            name = ""
            while self.peek() and self.peek() != ">":
                name += self.s[self.i]
                self.i += 1
            self.eat(">")
            if name not in self.macros:
                raise ParseError(f"unknown macro <{name}>")
            return self.macros[name]
        if c == "" or c in "*+?|){}":
            raise ParseError(f"unexpected {c!r} at {self.i} in {self.s!r}")
        self.i += 1
        if c not in self.alphabet:
            raise ParseError(f"symbol {c!r} outside alphabet {sorted(self.alphabet)}")
        return Sym([c])

    def charclass(self):
        self.eat("[")
        negate = False
        if self.peek() == "^":
            self.eat("^")
            negate = True
        chars = set()
        while self.peek() and self.peek() != "]":
            chars.add(self.s[self.i])
            self.i += 1
        self.eat("]")
        bad = chars - set(self.alphabet)
        if bad:
            raise ParseError(f"symbols {sorted(bad)} outside alphabet")
        if negate:
            chars = set(self.alphabet) - chars
        if not chars:
            raise ParseError("empty character class")
        return Sym(chars)


def parse_regex(text, alphabet, macros=None):
    return _Parser(text, tuple(alphabet), macros).parse()


# --------------------------------------------------------------------------
# Thompson construction
# --------------------------------------------------------------------------

class NFA:
    """Thompson NFA with epsilon closures folded into the transition table."""

    def __init__(self, pattern, alphabet, macros=None):
        self.pattern = pattern
        self.alphabet = tuple(alphabet)
        self._sym_edges = []            # state -> list[(frozenset chars, state)]
        self._eps_edges = []            # state -> list[state]
        ast = parse_regex(pattern, self.alphabet, macros)
        start, accept = self._build(ast)
        self.n_states = len(self._sym_edges)
        self._finalise(start, accept)

    # ---- construction -------------------------------------------------
    def _new_state(self):
        self._sym_edges.append([])
        self._eps_edges.append([])
        return len(self._sym_edges) - 1

    def _build(self, node):
        if isinstance(node, Eps):
            s = self._new_state()
            return s, s
        if isinstance(node, Sym):
            s = self._new_state()
            t = self._new_state()
            self._sym_edges[s].append((node.chars, t))
            return s, t
        if isinstance(node, Cat):
            start = last = None
            for part in node.parts:
                s, t = self._build(part)
                if start is None:
                    start = s
                else:
                    self._eps_edges[last].append(s)
                last = t
            if start is None:
                s = self._new_state()
                return s, s
            return start, last
        if isinstance(node, Alt):
            s = self._new_state()
            t = self._new_state()
            for part in node.parts:
                ps, pt = self._build(part)
                self._eps_edges[s].append(ps)
                self._eps_edges[pt].append(t)
            return s, t
        if isinstance(node, Star):
            s = self._new_state()
            t = self._new_state()
            bs, bt = self._build(node.body)
            self._eps_edges[s].append(bs)
            self._eps_edges[s].append(t)
            self._eps_edges[bt].append(bs)
            self._eps_edges[bt].append(t)
            return s, t
        raise TypeError(node)

    # ---- closures and tables -------------------------------------------
    def _closure_mask(self, states):
        seen = set()
        stack = list(states)
        while stack:
            q = stack.pop()
            if q in seen:
                continue
            seen.add(q)
            stack.extend(self._eps_edges[q])
        mask = 0
        for q in seen:
            mask |= 1 << q
        return mask

    def _finalise(self, start, accept):
        n = self.n_states
        self.accept_mask = self._closure_mask_reverse_eps(accept)
        self.start_mask = self._closure_mask([start])
        # per-symbol table: state -> mask of successors (epsilon-closed)
        # rows are built from the epsilon-closure of the *source* state too, so
        # every state's row already accounts for what is reachable by epsilon.
        closures = [self._closure_mask([q]) for q in range(n)]
        self.table = {}
        for ch in self.alphabet:
            row = [0] * n
            for q in range(n):
                targets = []
                m = closures[q]
                while m:
                    b = m & -m
                    p = b.bit_length() - 1
                    targets.extend(t for chars, t in self._sym_edges[p] if ch in chars)
                    m ^= b
                if targets:
                    row[q] = self._closure_mask(targets)
            self.table[ch] = row
        self._compute_distances()
        self._compute_always()

    def _closure_mask_reverse_eps(self, accept):
        """States that reach ``accept`` using epsilon edges only."""
        rev = [[] for _ in range(self.n_states)]
        for q, outs in enumerate(self._eps_edges):
            for t in outs:
                rev[t].append(q)
        seen = set()
        stack = [accept]
        while stack:
            q = stack.pop()
            if q in seen:
                continue
            seen.add(q)
            stack.extend(rev[q])
        mask = 0
        for q in seen:
            mask |= 1 << q
        return mask

    def _compute_distances(self):
        """dist[q] = fewest symbols from q to an accepting state (INF if none)."""
        n = self.n_states
        rev = [[] for _ in range(n)]
        for ch in self.alphabet:
            row = self.table[ch]
            for q in range(n):
                m = row[q]
                while m:
                    b = m & -m
                    rev[b.bit_length() - 1].append(q)
                    m ^= b
        dist = [INF] * n
        frontier = []
        for q in range(n):
            if (self.accept_mask >> q) & 1:
                dist[q] = 0
                frontier.append(q)
        d = 0
        while frontier:
            d += 1
            nxt = []
            for q in frontier:
                for p in rev[q]:
                    if dist[p] is INF or dist[p] > d:
                        if dist[p] == INF:
                            dist[p] = d
                            nxt.append(p)
            frontier = nxt
        self.dist = dist

    def _compute_always(self):
        """Greatest set A of accepting states with: for every symbol some
        successor stays in A.  A subset meeting A accepts for ever."""
        alive = set(q for q in range(self.n_states) if (self.accept_mask >> q) & 1)
        changed = True
        while changed:
            changed = False
            for q in list(alive):
                for ch in self.alphabet:
                    succ = self.table[ch][q]
                    ok = False
                    m = succ
                    while m:
                        b = m & -m
                        if (b.bit_length() - 1) in alive:
                            ok = True
                            break
                        m ^= b
                    if not ok:
                        alive.discard(q)
                        changed = True
                        break
        mask = 0
        for q in alive:
            mask |= 1 << q
        self.always_mask = mask

    # ---- runtime services ----------------------------------------------
    def step(self, mask, ch):
        row = self.table[ch]
        out = 0
        m = mask
        while m:
            b = m & -m
            out |= row[b.bit_length() - 1]
            m ^= b
        return out

    def accepts(self, mask):
        return bool(mask & self.accept_mask)

    def always(self, mask):
        return bool(mask & self.always_mask)

    def min_remaining(self, mask):
        best = INF
        m = mask
        while m:
            b = m & -m
            d = self.dist[b.bit_length() - 1]
            if d < best:
                best = d
                if best == 0:
                    return 0
            m ^= b
        return best
