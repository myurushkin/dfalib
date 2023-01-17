import random
import unittest
import regex
import rstr
import dafna
from dafna.lib.strength import hairpin

class TestHairpin(unittest.TestCase):
    def test_01(self):
        def hairpin_random_string(strength):
            n = random.randint(1, strength - 1)
            m = strength - n

            hairpin_head_pattern = f'((a|t){{{n}}})((g|c){{{m}}})'
            hairpin_loop_pattern = '(a|t){3,7}'
            hairpin_tail_pattern = '({gc_group}{at_group})'

            hairpin_head = rstr.xeger(hairpin_head_pattern)
            hairpin_loop = rstr.xeger(hairpin_loop_pattern)
            sub_groups = regex.findall(hairpin_head_pattern, hairpin_head)[0]
            hairpin_tail = rstr.xeger(hairpin_tail_pattern.format(
                gc_group=dafna.replace_complimentary_symbol(sub_groups[2][::-1]),
                at_group=dafna.replace_complimentary_symbol(sub_groups[0][::-1])
                )
            )

            return f'{hairpin_head}{hairpin_loop}{hairpin_tail}'

        hairpin_strings = [hairpin_random_string(n) for n in range(3, 20)]

        self.assertEqual(list(range(3, 20)), [dafna.hairpin_max_strength(hairpin) for hairpin in hairpin_strings])

    def test_02(self):
        values = [
            ('atatatatatatatatatatatatatatatatatatatatatatatatatatatatatat', 28),
            ('acgacgacgacgacgacgacgacgacgacgacgacgacgacgacgacgacgacgacgacg', 18),
            ('aaattaaattaaattaaattaaattaaattaaattaaattaaattaaattaaattaaatt', 23),

        ]

        for str_val, val in values:
            print(str_val)
            self.assertEqual(hairpin.max_hairpin_strength(str_val), val)