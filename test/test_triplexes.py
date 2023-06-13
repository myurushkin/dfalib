import unittest
import rstr
import dafna
from dafna.lib.strength.strength import triplex_max_strength

class TestTriplexes(unittest.TestCase):
    def test_01(self):
        values = [
            ('gcgcatcaaaggcactgtacagacggagttattcctcccagtctcctattgtaaccatca', 4),
            ('TCTCTCtttCTCTCTcccAGAGAG', 6),
            ('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 0),
            ('TcccAcccT', 1),
            ('AGAGAGAACCCCTTCTCTCTTATATCTGTCTT', 8)
        ]

        for str_val, val in values:
            result, _ = triplex_max_strength(str_val)
            self.assertEqual(result, val)
            