import random
import unittest
import rstr
import dafna


class TestFirst(unittest.TestCase):
    def test_00(self):
        values = [
            ('ggaggaggaggaggaggaggagg', 2),
            ('ggggggggggg', 2),
            ('ggaggaggagg', 2),
            ('ggaggaggaga', 0),
        ]

        for str_val, val in values:
            self.assertEqual(dafna.gqd_max_strength(str_val), val)

    def test01(self):
        for x in range(2, 10):
            value = ('g' * x).join([rstr.rstr('act') for _ in range(5)])
            self.assertEqual(dafna.gqd_max_strength(value), x)

    def test02(self):
        for x in range(12, 20):
            value = ('g' * x).join([rstr.rstr('act') for _ in range(2)])
            self.assertEqual(dafna.gqd_max_strength(value), (x - 3)//4)