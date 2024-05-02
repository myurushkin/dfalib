import random
import unittest
import rstr
from dafna.lib.strength import gqd_canonical

class TestGQDCanonical(unittest.TestCase):
    def test_00(self):
        values = [
            ('cgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcg', 0),
            ('gggcgggagggtagcggggggc', 3),
            ('gagaggtgagaggcg', 2),
            ('ggaggaggagcg', 2),
            ('ggaggaggaggaggaggaggagg', 2),
            ('ggggggggggg', 2),
            ('ggaggaggagg', 2),
            ('ggaggaggaga', 0),
        ]

        for str_val, val in values:
            self.assertEqual(gqd_canonical.gqd_max_strength(str_val), val)

    def test01(self):
        for x in range(2, 10):
            value = ('g' * x).join([rstr.rstr('act') for _ in range(5)])
            self.assertEqual(gqd_canonical.gqd_max_strength(value), x)

    def test02(self):
        for x in range(12, 20):
            value = ('g' * x).join([rstr.rstr('act') for _ in range(2)])
            self.assertEqual(gqd_canonical.gqd_max_strength(value), (x - 3)//4)

    def test03(self):
        for _ in range(1000):
            input_string = rstr.rstr('acgt', random.randint(15, 40))
            self.assertEqual(gqd_canonical.gqd_max_strength(input_string), gqd_canonical.gqd_max_strength_naive(input_string))