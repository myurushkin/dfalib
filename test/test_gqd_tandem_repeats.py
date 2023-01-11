import random
import unittest
import rstr
from dafna.lib.strength import gqd_tandem_repeats

class TestGQDTandemRepeats(unittest.TestCase):
    def test_00(self):
        values = [
            ('ggaggaggaga', 0),
            ('ggaggaggagg', 2),
            ('ggggggggggg', 2),
            ('cgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcgcg', 7),
            ('ggaggaggaggaggaggaggagg', 4),

            # ('gggcgggagggtagcggggggc', 0),
            # ('gagaggtgagaggcg', 2),
            # ('ggaggaggagcg', 2),
        ]

        for str_val, val in values:
            print(str_val)
            self.assertEqual(gqd_tandem_repeats.max_strength(str_val), val)

    # def test01(self):
    #     for x in range(2, 10):
    #         value = ('g' * x).join([rstr.rstr('act') for _ in range(5)])
    #         self.assertEqual(gqd_tandem_repeats.max_strength(value), x)
    #
    # def test02(self):
    #     for x in range(12, 20):
    #         value = ('g' * x).join([rstr.rstr('act') for _ in range(2)])
    #         self.assertEqual(gqd_tandem_repeats.max_strength(value), (x - 3)//4)

    # def test03(self):
    #     for _ in range(1000):
    #         input_string = rstr.rstr('acgt', random.randint(15, 40))
    #         self.assertEqual(gqd_tandem_repeats.max_strength(input_string), gqd_canonical.gqd_max_strength_naive(input_string))