import unittest
import dafna

class TestFirst(unittest.TestCase):
    def test_01(self):
        ctx = dafna.Context()

        X = ctx.create_pattern("a|c|g|t", simple=True, name="X")
        self.assertEqual(3, dafna.max_gquadruplex_strength('TTGGATCTGAGAATCAGATGTGGGTGGGTGGGT'.lower()))