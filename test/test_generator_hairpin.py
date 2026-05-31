import unittest

from dafna.lib.generation import hairpin_gen, triplexes_gen
from dafna.lib.strength.hairpin import max_hairpin_strength
from dafna.lib.strength.triplex import triplex_max_strength
from dafna.shared import Context, pintersect, psum


class TestGeneratorHairpin(unittest.TestCase):
    def test_canonical_strengths(self):
        for strength in (2, 3, 4):
            ctx = Context()
            ctx.create_pattern("a|c|g|t", simple=True, name="X")
            result = pintersect(psum(hairpin_gen.create(strength, ctx)))
            vals = [max_hairpin_strength(s) for i, s in enumerate(result.min_strings()) if i < 60]
            self.assertTrue(vals, f"strength {strength} produced no strings")
            self.assertTrue(all(v == strength for v in vals), f"{strength}: {set(vals)}")


class TestGeneratorTriplex(unittest.TestCase):
    def test_canonical_strengths(self):
        for strength in (1, 2, 3):
            ctx = Context()
            ctx.create_pattern("a|c|g|t", simple=True, name="X")
            result = pintersect(psum(triplexes_gen.create(strength, ctx)))
            vals = [triplex_max_strength(s)[0] for i, s in enumerate(result.min_strings()) if i < 60]
            self.assertTrue(vals, f"strength {strength} produced no strings")
            self.assertTrue(all(v == strength for v in vals), f"{strength}: {set(vals)}")


if __name__ == "__main__":
    unittest.main()
