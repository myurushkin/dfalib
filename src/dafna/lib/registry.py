"""Registry of searchable DNA secondary structures.

A :class:`StructureDef` is the single source of truth for one structure: its
topologies (each with a generator), an optional strength function, and the simple
patterns its generators need registered in a :class:`~dafna.shared.Context`.

Built-in structures (GQD, IMT, HRP, TRX) are registered on import. Plugins and
inline ``&CUSTOM`` config blocks add more via :func:`register` /
:func:`make_template_structure`.

Two ways a structure's strength is measured for an arbitrary string:

* ``strength_fn`` — a direct measurement (all built-ins provide one).
* membership — for generator-only structures (templates, generator-only
  plugins): :func:`membership_strength` finds the largest ``s`` in a range whose
  generated automaton accepts the string.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from dafna.shared import Automata, Context, pintersect, psum

# generator: (strength, ctx) -> list[Automata]
GeneratorFn = Callable[[int, Context], list]
# strength: (string) -> number
StrengthFn = Callable[[str], float]


class RegistryError(Exception):
    """Raised on duplicate or unknown structure registration/lookup."""


@dataclass
class StructureDef:
    name: str
    generators: dict[str, GeneratorFn]
    strength_fn: Optional[StrengthFn] = None
    required_simple: dict[str, str] = field(default_factory=lambda: {"X": "a|c|g|t"})
    description: str = ""

    @property
    def topologies(self) -> list[str]:
        return list(self.generators)

    def make_context(self) -> Context:
        """A fresh Context with this structure's simple patterns registered."""
        ctx = Context()
        for simple_name, regex in self.required_simple.items():
            ctx.create_pattern(regex, simple=True, name=simple_name)
        return ctx


_REGISTRY: dict[str, StructureDef] = {}


def register(structure: StructureDef, *, replace: bool = False) -> StructureDef:
    """Register a structure. Raises unless ``replace`` if the name is taken."""
    key = structure.name.upper()
    if key in _REGISTRY and not replace:
        raise RegistryError(
            f"structure '{structure.name}' already registered (pass replace=True to override)"
        )
    if not structure.generators:
        raise RegistryError(f"structure '{structure.name}' has no generators")
    _REGISTRY[key] = structure
    return structure


def unregister(name: str) -> None:
    _REGISTRY.pop(name.upper(), None)


def get(name: str) -> StructureDef:
    try:
        return _REGISTRY[name.upper()]
    except KeyError:
        raise RegistryError(f"unknown structure '{name}'") from None


def is_registered(name: str) -> bool:
    return name.upper() in _REGISTRY


def all_names() -> list[str]:
    return [s.name for s in _REGISTRY.values()]


def topologies_by_name() -> dict[str, list[str]]:
    """Map every registered structure name -> its topology list (for the parser)."""
    return {s.name.upper(): s.topologies for s in _REGISTRY.values()}


def make_template_structure(
    name: str,
    template: str,
    *,
    strength_fn: Optional[StrengthFn] = None,
    required_simple: Optional[dict[str, str]] = None,
    topology: str = "canonical",
    description: str = "",
) -> StructureDef:
    """Build (but do not register) a StructureDef from a strength template."""
    # Imported here so the lightweight config path need not import generation.
    from dafna.lib.generation.template import make_template_generator

    return StructureDef(
        name=name,
        generators={topology: make_template_generator(template)},
        strength_fn=strength_fn,
        required_simple=required_simple or {"X": "a|c|g|t"},
        description=description,
    )


def accepts(automaton: Automata, ctx: Context, string: str) -> bool:
    """Whether ``automaton`` accepts exactly ``string`` (engine membership test).

    Built by intersecting with a literal automaton for ``string``; the result's
    minimal strings are ``[string]`` iff it is accepted.
    """
    literal = ctx.create_pattern("".join(string))
    intersection = automaton.intersect(literal).minimize()
    for value in intersection.min_strings():
        return value == string
    return False


def membership_strength(structure: StructureDef, string: str, str_min: int, str_max: int) -> int:
    """Largest strength in ``[str_min, str_max]`` whose generator accepts ``string``.

    Returns 0 if none match. Used to measure generator-only structures.
    """
    for strength in range(str_max, str_min - 1, -1):
        for topology in structure.topologies:
            ctx = structure.make_context()
            patterns = structure.generators[topology](strength, ctx)
            automaton = pintersect(psum(patterns))
            if accepts(automaton, ctx, string):
                return strength
    return 0


def _register_builtins() -> None:
    """Register GQD, IMT, HRP, TRX. Idempotent."""
    if _REGISTRY:
        return
    from dafna.lib.generation import (
        gqd_canonical_gen,
        gqd_tandem_repeats_gen,
        hairpin_gen,
        i_motif_gen,
        triplexes_gen,
    )
    from dafna.lib.strength.hairpin import max_hairpin_strength
    from dafna.lib.strength.strength import gqd_max_strength, i_motif_max_strength
    from dafna.lib.strength.triplex import triplex_max_strength

    def imt_canonical(strength: int, ctx: Context) -> list:
        # Canonical i-motif of strength s: n = m = s, minimal loops a=b=c=1.
        return i_motif_gen.create(n=strength, m=strength, a=1, b=1, c=1, ctx=ctx)

    register(StructureDef(
        name="GQD",
        generators={
            "canonical": gqd_canonical_gen.create,
            "tandem": gqd_tandem_repeats_gen.create,
        },
        strength_fn=gqd_max_strength,
        required_simple={"X": "a|c|g|t", "Y": "a|c|t"},
        description="G-quadruplex",
    ))
    register(StructureDef(
        name="IMT",
        generators={"canonical": imt_canonical},
        strength_fn=i_motif_max_strength,
        description="i-motif",
    ))
    register(StructureDef(
        name="HRP",
        generators={"canonical": hairpin_gen.create},
        strength_fn=max_hairpin_strength,
        description="hairpin",
    ))
    register(StructureDef(
        name="TRX",
        generators={"canonical": triplexes_gen.create},
        strength_fn=lambda string: triplex_max_strength(string)[0],
        description="triplex",
    ))


_register_builtins()
