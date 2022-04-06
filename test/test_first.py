import random
import unittest
import rstr
import pprint
import dafna


class TestFirst(unittest.TestCase):
    def test_01(self):
        generator = range(2, 21)

        def gqd_random_string(g_count):
            y = '(a|c|t){0,4}'
            x = '(a|c|t|g)'
            g_group_size = "Y*".join(['g'] * g_count)
            pattern = "X*" + "#" + "X+".join([g_group_size] * 4) + "#|" + "X*"
            pattern = pattern.replace("X", x)
            select_parts_pattern_for_dilute = random.sample(range(0, 4), k=3)
            while True:
                select_parts_pattern_for_dilute = [random.randint(0, 1) for _ in range(0, 4)]
                if not all(select_parts_pattern_for_dilute):
                    break

            parts_pattern = pattern.split('+', -1)
            pattern = '+'.join([part.replace('Y*', y) if
                                select_parts_pattern_for_dilute[idx] else part.replace('Y*', '') for idx, part in
                                enumerate(parts_pattern)])
            return rstr.xeger(pattern)

        gqd_strings = [gqd_random_string(n) for n in generator]
        gqd_strings_strength = [dafna.max_gquadruplex_strength(gqd) for gqd in gqd_strings]
        pprint.pprint(dict(zip(gqd_strings,  gqd_strings_strength)), sort_dicts=False)
        self.assertEqual(list(generator), gqd_strings_strength)
