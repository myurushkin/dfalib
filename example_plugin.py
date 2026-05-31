"""Example dafna plugin.

Importing this module registers a new structure, ``POLYA``, into the dafna
registry. After that it behaves exactly like a built-in: it can be enabled with a
``&POLYA`` block, generated, and (because it ships a strength function) measured
in scan mode.

Use it with::

    dafna run myconfig.conf --plugin example_plugin.py

or by adding ``PLUGIN=example_plugin.py`` to the ``&GEN`` block.
"""
from dafna.lib.generation.template import make_template_generator
from dafna.lib.registry import StructureDef, register


def polya_strength(string: str) -> int:
    """Strength = length of the longest run of consecutive 'a's."""
    best = run = 0
    for char in string.lower():
        run = run + 1 if char == "a" else 0
        best = max(best, run)
    return best


register(StructureDef(
    name="POLYA",
    # A poly-A tract of length s, surrounded by anything: X* a{s} X*
    generators={"canonical": make_template_generator("X* a{s} X*")},
    strength_fn=polya_strength,
    description="poly-A run (example plugin)",
))
