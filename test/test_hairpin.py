import random
import unittest

import regex
import rstr
import pprint
import dafna


class TestHairpin(unittest.TestCase):
    def test_01(self):
        generator = range(2, 21)

        def hairpin_random_string(strength):
            n = random.randint(1, strength)
            m = strength - n

            def replace_complimentary_symbol(string):
                repl = {'a': 't', 't': 'a', 'g': 'c', 'c': 'g'}
                replacement = dict((regex.escape(k), v) for k, v in repl.items())
                pattern = regex.compile("|".join(replacement.keys()))
                return "".join(list(pattern.sub(lambda m: replacement[regex.escape(m.group(0))], string)))

            hairpin_head_pattern = f'(((a|t){{{n}}})(a|t|g|c){{1,3}}((g|c){{{m}}}))'
            hairpin_loop_pattern = '(a|t){3,7}'
            hairpin_tail_pattern = '({gc_group}(a|c|g|t){{1,3}}{at_group})'

            hairpin_head = rstr.xeger(hairpin_head_pattern)
            hairpin_loop = rstr.xeger(hairpin_loop_pattern)
            sub_groups = regex.findall(hairpin_head_pattern, hairpin_head)[0]
            hairpin_tail = rstr.xeger(hairpin_tail_pattern.format(
                gc_group=replace_complimentary_symbol(sub_groups[4][::-1]),
                at_group=replace_complimentary_symbol(sub_groups[1][::-1])
            )
            )

            return f'{hairpin_head}{hairpin_loop}{hairpin_tail}'

        def hairpin_max_strength(string):
            def replace_complimentary_symbol(string):
                repl = {'a': 't', 't': 'a', 'g': 'c', 'c': 'g'}
                replacement = dict((regex.escape(k), v) for k, v in repl.items())
                pattern = regex.compile("|".join(replacement.keys()))
                return "".join(list(pattern.sub(lambda m: replacement[regex.escape(m.group(0))], string)))
            strength = 0
            n_count = '1,'
            m_count = '1,'
            pattern = \
                '(({at_group})[a|t|g|c]{{1,3}}({gc_group})[a|t|g|c]{{3,7}}({gc_complimentary_group})[a|t|g|c]{{1,3}}({at_complimentary_group}))'
            start_pattern = '(([a|t]{{{n_count}}})[a|t|g|c]{{1,3}}([g|c]{{{m_count}}}))[a|t|g|c]{{3,7}}([g|c]{{1,}})'
            match = regex.findall(start_pattern.format(n_count=n_count, m_count=m_count), string)
            if any(match):
                for hairpin_head_part in match:
                    sub_strength = len(hairpin_head_part[1]) + len(hairpin_head_part[2])
                    n = len(hairpin_head_part[1])
                    for i in range(n, 0, -1):
                        sub_match = regex.findall(start_pattern.format(n_count=i, m_count=m_count), string)
                        if any(sub_match):
                            at_group, at_complimentary_group = sub_match[0][1], replace_complimentary_symbol(sub_match[0][1])
                            gc_group, gc_complimentary_group = sub_match[0][2], replace_complimentary_symbol(sub_match[0][2][::-1])
                            full_match = regex.findall(pattern.format(
                                    gc_group=gc_group,
                                    gc_complimentary_group=gc_complimentary_group,
                                    at_group=at_group,
                                    at_complimentary_group=at_complimentary_group
                                ),
                                string
                            )

                            if any(full_match):
                                temp_strength = len(full_match[0][1]) + len(full_match[0][2])
                                sub_strength = sub_strength if sub_strength > temp_strength else temp_strength

                    strength = strength if strength > sub_strength else sub_strength
            return strength
        print(hairpin_random_string(3))
        print(hairpin_max_strength(hairpin_random_string(3)))

    def test_02(self):
        generator = [2, 3, 4, 5]

        gqd_strings = [
            'accattcacccgggaaggtagggcaaactccattcacccttctggaacacctcaacaattattactactactatatccggggcaaactaaaccctttaacctccactctgtttacaatccaaaaatctattctctatcctcgaacgcttcctacacatacaattatttcggctttatcccaccataactccttcttcattcatttgagctaccttcaatttatacattaacatccctcactcctgactatcacaagaacacattcaccaggatacaattcataaagaacttccccttatcatccagtctcactacaa',
            'cttccacataaactatggtacacttttttttttctcttaaagggtcaaacccccaaaaatccttctccgaaaaaaggctacttggcaaaaccccaaccccattttctccatcccatataactactagttctgatgctaaccactcacacacccaatatatttccaaacttcaatcactctttttcacctaagggtttcctatcccaaattacacttcctttgggactaccctatattaaaattccaactcccacccatcatcaccactaatattccc',
            'ctcttttcattctacagggtctctatcacataacctcttattttcttataccattccttacccgctcaggtgcaatccattcatacaaaaatttcaacacttcaaactctggggacactctacactactttacacaactccttataccatcacatctcatttccacctattcctatttcattattccattatataattacaccaccaggggacactctacccaattcctttgctcctcctctacccaaaaagtttacttctcaacaggggtcatcctcatcagatataac',
            'acccacatttactgacaacaactcccaacttgtgagtctccattcaatcttataaatatcaaatatcaaatataatcaaaacttaatcctttcagggggcccaatatatataatgatgacagtatcgtccgcccaactttaacactcacttccaatatcaatcttcattcccctaattcaccccctcactatacttaattagtgctgtactgctgtacttctttctccgttataaaacctttataaccgcttcataaaactatcccaatatttatatcatttctaacccctaacttaatcctaattttttagcgcactgtaagttgaaaactactacttatttatcctaaaacactttcacaacacccaacctttctctcttttatcactcttaagatcacattctagactcccctttca',
        ]

        gqd_strings_strength = [dafna.gqd_max_strength(gqd) for gqd in gqd_strings]
        # pprint.pprint(dict(zip(gqd_strings,  gqd_strings_strength)), sort_dicts=False)
        self.assertEqual(generator, gqd_strings_strength)
