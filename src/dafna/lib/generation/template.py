"""Strength-parameterised pattern templates for user-defined structures.

A template is an ordinary engine pattern (``*``, ``+``, ``?``, ``|``, groups,
literals and registered simple-pattern names like ``X``) plus *count
placeholders* in braces that depend on the strength ``s``::

    X* g{s} X+ g{s} X+ g{s} X+ g{s} X*      # a quadruplex parameterised by s
    X* (gc){2*s} X*                          # a 'gc' repeat, 2*s copies

The engine does NOT support regex counted quantifiers (``g{3}`` matches garbage),
so a count ``atom{expr}`` is expanded to literal repetition *in Python* before
the pattern reaches the engine. ``atom`` is the immediately preceding single
character or parenthesised ``(...)`` group; ``expr`` may use ``s``, integers and
``+ - *`` (e.g. ``{s}``, ``{s+1}``, ``{2*s}``).
"""
import re

from dafna.lib.generation import preprocess_pattern

# An atom (a parenthesised group without nesting, or a single non-space,
# non-brace char) immediately followed by a {count expression}.
_COUNT_ATOM = re.compile(r"(\([^()]*\)|[^\s{}])\s*\{([^}]*)\}")

# Only digits, the variable s, arithmetic operators and spaces are allowed in a
# count expression; this guard makes the subsequent eval safe.
_SAFE_EXPR = re.compile(r"[0-9s+\-*\s]+")


class TemplateError(Exception):
    """Raised on a malformed template or count expression."""


def _eval_count(expr: str, strength: int) -> int:
    expr = expr.strip()
    if not expr or not _SAFE_EXPR.fullmatch(expr):
        raise TemplateError(f"invalid count expression '{{{expr}}}'")
    try:
        value = eval(expr, {"__builtins__": {}}, {"s": int(strength)})  # noqa: S307 - guarded
    except Exception as exc:  # pragma: no cover - guard already restricts input
        raise TemplateError(f"cannot evaluate count expression '{{{expr}}}': {exc}") from None
    count = int(value)
    if count < 0:
        raise TemplateError(f"count expression '{{{expr}}}' evaluated to {count} < 0")
    return count


def _expand_one(match: "re.Match", strength: int) -> str:
    atom, expr = match.group(1), match.group(2)
    count = _eval_count(expr, strength)
    unit = atom[1:-1] if atom.startswith("(") else atom
    return unit * count


def expand_template(template: str, strength: int) -> str:
    """Expand every ``atom{expr}`` count in ``template`` for the given strength.

    Returns the expanded, still-spaced pattern (run :func:`preprocess_pattern`
    afterwards to feed the engine).
    """
    current = template
    for _ in range(100):  # bounded; each pass resolves one nesting level
        nxt = _COUNT_ATOM.sub(lambda m: _expand_one(m, strength), current)
        if nxt == current:
            break
        current = nxt
    if "{" in current or "}" in current:
        raise TemplateError(f"unresolved count braces after expansion: {current!r}")
    return current


def make_template_generator(template: str):
    """Return a ``create(strength, ctx)`` generator for a strength template."""

    def create(strength: int, ctx):
        pattern = preprocess_pattern(expand_template(template, strength))
        return [ctx.create_pattern(pattern)]

    return create
