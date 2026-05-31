import unittest
from dafna.lib.generation import i_motif_gen
from dafna.shared import *


class TestGeneratorIMotif(unittest.TestCase):
    def test_00_canonical_simple(self):
        n = 3
        m = 2
        a = 2
        b = 3
        c = 3

        ctx = Context()
        # Authoritative convention (see scripts/measure_second.py): the caller
        # registers X = a|c|g|t so generator fillers span the full alphabet.
        X = ctx.create_pattern("a|c|g|t", simple=True, name="X")
        patterns = i_motif_gen.create(n=n, m=m, a=a, b=b, c=c, ctx=ctx)
        result: Automata = pintersect(psum(patterns))

        # Every generated string contains an i-motif of at least the target
        # strength; X-fillers may add C's and only strengthen it, so assert >=.
        # The weakest generated string realises exactly the target strength.
        # NOTE: одна пара CC = 0.5
        target = (n + m) / 2
        strengths = [i_motif_max_strength(s) for s in result.min_strings()]
        self.assertTrue(all(v >= target for v in strengths))
        self.assertEqual(min(strengths), target)
