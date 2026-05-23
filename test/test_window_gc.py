"""
Biocase tests using find_min_string_in_gc_window (Week 4).

Three biological scenarios demonstrating end-to-end use of the GC-window layer
on real DNA pattern constraints (hairpin, primer, G-quadruplex canonical).

Test invocation:
  PYTHONPATH=dfalib/src .venv/bin/python -m unittest dfalib.test.test_window_gc -v
or via discover:
  PYTHONPATH=dfalib/src .venv/bin/python -m unittest discover -s dfalib/test -v
"""

import unittest

from dafna.shared import Context
from dafna.window import find_min_string_in_gc_window
from dafna.lib.generation import gqd_canonocal_gen
from dafna.lib.strength.hairpin import max_hairpin_strength
from dafna.lib.strength.gqd_canonical import gqd_max_strength


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ctx():
    ctx = Context()
    ctx.create_pattern('a|c|g|t', simple=True, name='X')
    return ctx


def _gc_frac(s):
    return sum(c in 'gc' for c in s) / len(s)


def _one(n=1):
    """Return regex for exactly n unconstrained DNA characters."""
    return '(a|c|g|t)' * n


def _build_hairpin_dfa(ctx, stems_and_rcs, loop_lens):
    """
    Union DFA over all (stem, revcomp_stem, loop_len) combinations.

    Each variant accepts strings of the form  stem + (loop_len chars) + revcomp_stem,
    guaranteeing the stem arm is complementary to the 3'-arm.
    """
    patterns = []
    for stem, rc in stems_and_rcs:
        for ll in loop_lens:
            patterns.append(ctx.create_pattern(stem + _one(ll) + rc))
    result = patterns[0].minimize()
    for p in patterns[1:]:
        result = result.add(p).minimize()
    return result


# ---------------------------------------------------------------------------
# §6.1 — Hairpin with GC-window
# ---------------------------------------------------------------------------

class TestGCWindowHairpin(unittest.TestCase):
    """
    Build a hairpin DFA: (stem)(loop)(revcomp(stem)).
    stem lengths 4-6, loop lengths 4-7.

    Stems are chosen so each arm contributes ~2 GC bases, keeping total GC
    fraction in the achievable range for the [0.4, 0.6] window.

    Stems used:
      n=4: 'acgt' / 'acgt'  (palindrome, 2 GC each arm)
      n=5: 'aacgt' / 'acgtt' (2 GC each arm)
      n=6: 'aaacgt' / 'acgttt' (2 GC each arm)
    """

    # (stem, revcomp_stem) pairs — each has 2 GC bases per arm
    STEMS_AND_RCS = [
        ('acgt',   'acgt'),
        ('aacgt',  'acgtt'),
        ('aaacgt', 'acgttt'),
    ]
    LOOP_LENS = list(range(4, 8))      # 4,5,6,7
    ALPHA, BETA = 0.4, 0.6
    LENGTH_CAP = 60

    def test_gc_window_hairpin(self):
        ctx = _make_ctx()
        big = _build_hairpin_dfa(ctx, self.STEMS_AND_RCS, self.LOOP_LENS)
        result = find_min_string_in_gc_window(big, self.ALPHA, self.BETA,
                                              self.LENGTH_CAP)
        self.assertIsNotNone(result,
            "find_min_string_in_gc_window returned None for hairpin DFA")

        # Total length must be within expected bounds: min = 4+4 + 4 = 12, max = 6+6 + 7 = 19
        self.assertGreaterEqual(len(result), 12,
            f"Result too short: {result!r}")
        self.assertLessEqual(len(result), 19,
            f"Result too long: {result!r}")

        # Whole-string GC fraction must lie in [alpha, beta]
        gc = _gc_frac(result)
        self.assertGreaterEqual(gc, self.ALPHA,
            f"GC fraction {gc:.3f} below alpha={self.ALPHA}: {result!r}")
        self.assertLessEqual(gc, self.BETA,
            f"GC fraction {gc:.3f} above beta={self.BETA}: {result!r}")

        # The string must be accepted by one of the hairpin patterns:
        # verify stem + loop + revcomp structure
        matched = False
        for stem, rc in self.STEMS_AND_RCS:
            n = len(stem)
            if (len(result) >= n + 4 + n and
                    result[:n] == stem and result[-n:] == rc):
                matched = True
                break
        self.assertTrue(matched,
            f"Result {result!r} does not match any (stem, loop, revcomp) pattern")

        # Hairpin strength ≥ stem_len confirms complementary pairing
        matched_stem_len = len(stem) if matched else 0
        strength = max_hairpin_strength(result)
        self.assertGreaterEqual(strength, matched_stem_len,
            f"Hairpin strength {strength} < stem_len {matched_stem_len}: {result!r}")


# ---------------------------------------------------------------------------
# §6.2 — Primer with GC-window
# ---------------------------------------------------------------------------

class TestGCWindowPrimer(unittest.TestCase):
    """
    Build a primer DFA: length in [18, 25], GC% in [0.4, 0.6].

    The DFA accepts strings of exactly 18 characters (the shortest acceptable
    primer). The GC window is applied globally via find_min_string_in_gc_window.
    The 'no hairpin > 4' constraint is verified post-hoc on the returned string.

    Using a length-18 DFA (minimum primer length) guarantees find_min_string
    returns the shortest valid primer, which is most likely to have low hairpin
    strength due to the greedy BFS nature of the search.
    """

    LENGTH = 18       # minimum primer length
    ALPHA, BETA = 0.4, 0.6
    LENGTH_CAP = 30
    MAX_HAIRPIN = 4   # no internal hairpin longer than 4 allowed

    def test_gc_window_primer(self):
        ctx = _make_ctx()
        big = ctx.create_pattern(_one(self.LENGTH))
        result = find_min_string_in_gc_window(big, self.ALPHA, self.BETA,
                                              self.LENGTH_CAP)
        self.assertIsNotNone(result,
            "find_min_string_in_gc_window returned None for primer DFA")

        # Length must be in [18, 25]
        self.assertGreaterEqual(len(result), 18,
            f"Primer too short: {result!r}")
        self.assertLessEqual(len(result), 25,
            f"Primer too long: {result!r}")

        # GC fraction must lie in [alpha, beta]
        gc = _gc_frac(result)
        self.assertGreaterEqual(gc, self.ALPHA,
            f"GC fraction {gc:.3f} below alpha={self.ALPHA}: {result!r}")
        self.assertLessEqual(gc, self.BETA,
            f"GC fraction {gc:.3f} above beta={self.BETA}: {result!r}")

        # No internal hairpin longer than MAX_HAIRPIN (checked post-hoc)
        strength = max_hairpin_strength(result)
        self.assertLessEqual(strength, self.MAX_HAIRPIN,
            f"Hairpin strength {strength} > {self.MAX_HAIRPIN}: {result!r}")

        # All characters must be DNA alphabet
        self.assertTrue(all(c in 'acgt' for c in result),
            f"Non-DNA character in {result!r}")


# ---------------------------------------------------------------------------
# §6.3 — G-quadruplex canonical with GC-window
# ---------------------------------------------------------------------------

class TestGCWindowGQDCanonical(unittest.TestCase):
    """
    Build a canonical G-quadruplex DFA using gqd_canonocal_gen (strength=3:
    four runs of ≥3 G's separated by non-empty loops).

    Apply GC-window [0.5, 0.8] globally via find_min_string_in_gc_window.
    G-quadruplex sequences are inherently GC-rich so [0.5, 0.8] is achievable.

    Verification post-hoc: gqd_max_strength(result) ≥ 3.
    """

    GQD_STRENGTH = 3
    ALPHA, BETA = 0.5, 0.8
    LENGTH_CAP = 100

    def test_gc_window_gqd_canonical(self):
        ctx = _make_ctx()
        gqd_patterns = gqd_canonocal_gen.create(self.GQD_STRENGTH, ctx)
        self.assertEqual(len(gqd_patterns), 1,
            "gqd_canonocal_gen.create expected to return list of 1 pattern")
        big = gqd_patterns[0]

        result = find_min_string_in_gc_window(big, self.ALPHA, self.BETA,
                                              self.LENGTH_CAP)
        self.assertIsNotNone(result,
            "find_min_string_in_gc_window returned None for GQD canonical DFA")

        # GC fraction must lie in [alpha, beta]
        gc = _gc_frac(result)
        self.assertGreaterEqual(gc, self.ALPHA,
            f"GC fraction {gc:.3f} below alpha={self.ALPHA}: {result!r}")
        self.assertLessEqual(gc, self.BETA,
            f"GC fraction {gc:.3f} above beta={self.BETA}: {result!r}")

        # String must contain a valid G-quadruplex of strength >= GQD_STRENGTH
        strength = gqd_max_strength(result)
        self.assertGreaterEqual(strength, self.GQD_STRENGTH,
            f"GQD strength {strength} < {self.GQD_STRENGTH}: {result!r}")

        # Must have at least 4 G-runs of length >= GQD_STRENGTH
        import re
        g_runs = re.findall(r'g+', result)
        long_runs = [r for r in g_runs if len(r) >= self.GQD_STRENGTH]
        self.assertGreaterEqual(len(long_runs), 4,
            f"Fewer than 4 G-runs of length >= {self.GQD_STRENGTH}: {result!r}")

        # All characters must be DNA alphabet
        self.assertTrue(all(c in 'acgt' for c in result),
            f"Non-DNA character in {result!r}")


if __name__ == '__main__':
    unittest.main()
