import random
import unittest
import rstr
import pprint
import dafna


class TestTriplexes(unittest.TestCase):
    def test_01(self):
        generator = range(2, 21)

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

        a = triplex_random_string(2)
        pprint.pprint(a)

        # self.assertEqual(list(generator), gqd_strings_strength)

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
