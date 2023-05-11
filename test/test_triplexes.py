import unittest
import rstr
import dafna
from dafna.lib.strength.strength import triplex_max_strength

class TestTriplexes(unittest.TestCase):
    def test_01(self):
        values = [
            ('TcccAcccT', 1),
            ('TCTCTCtttCTCTCTcccAGAGAG', 6),
            ('AGAGAGAACCCCTTCTCTCTTATATCTGTCTT', 8)
        ]

        for str_val, val in values:
            print(str_val)
            self.assertEqual(triplex_max_strength(str_val), val)