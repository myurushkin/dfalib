import itertools
import random
import unittest

import regex
import rstr
import pprint
import dafna


class TestTriplexes(unittest.TestCase):
    def test_01(self):
        generator = range(2, 4)

        def triplex_random_string(count):
            x_group = '(a|c|g|t)'
            triplex_views = [
                '{A}{{{count}}}{X}{{4}}{C}{{{count}}}{X}{{3}}{B}{{{count}}}',
                '{A}{{{count}}}{X}{{3}}{B}{{{count}}}{X}{{3}}{C}{{{count}}}',
            ]
            triplex_groups_options = [
                {'A': '(t|c)', 'B': 'a', 'C': 't'},
                {'A': '(c|g|a)', 'B': 'g', 'C': 'c'},
                {'A': '(g)', 'B': 't', 'C': 'a'},
                {'A': '(t|c)', 'B': 'c', 'C': 'g'},
            ]
            patterns = [
                view.format(X=x_group, count=count, **triplex_items) for view in triplex_views
                for triplex_items in triplex_groups_options
            ]

            return [rstr.xeger(triplex) for triplex in patterns]

        # a = triplex_random_string(2)
        # pprint.pprint(a)

        def triplex_max_strength(string):
            x_group = '[a|c|g|t]'
            triplex_forms = [
                '{A}{{{count}}}{X}{{4,}}{C}{{{count}}}{X}{{3,}}{B}{{{count}}}',
                '{A}{{{count}}}{X}{{3,}}{B}{{{count}}}{X}{{3,}}{C}{{{count}}}',
            ]
            triplex_groups_options = [
                {'A': '[t|c]', 'B': 'a', 'C': 't'},
                {'A': '[c|g|a]', 'B': 'g', 'C': 'c'},
                {'A': 'g', 'B': 't', 'C': 'a'},
                {'A': '[t|c]', 'B': 'c', 'C': 'g'},
            ]
            strength = 0
            for triplex_form in triplex_forms:
                groups = '({item}{{1,}})'
                for triplex_item in triplex_groups_options:
                    b_match = regex.findall(groups.format(item=triplex_item['B']), string)
                    c_match = regex.findall(groups.format(item=triplex_item['C']), string)
                    if c_match and b_match:
                        start_count_n = min(
                            [max([len(b_gr) for b_gr in b_match]), max([len(c_gr) for c_gr in c_match])]
                        )
                        for i in range(start_count_n, 1, -1):
                            triplex_match = regex.findall(
                                triplex_form.format(count=i, X=x_group, A=triplex_item['A'], B=triplex_item['B'],
                                                    C=triplex_item['C']), string)
                            if any(triplex_match):
                                strength = strength if strength > i else i

            return strength

        a = triplex_random_string(2) + triplex_random_string(3) + triplex_random_string(4)
        # pprint.pprint(a)
        pprint.pprint([item for item in zip(a, [triplex_max_strength(s) for s in a])])

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
