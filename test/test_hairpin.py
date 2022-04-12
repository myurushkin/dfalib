import random
import unittest
import rstr
import pprint
import dafna


class TestHairpin(unittest.TestCase):
    def test_01(self):
        generator = range(2, 21)

        def i_motif_random_string(n, m, biological_significance=False):
            x_group = '(a|c|g|t)'
            y_symbol = '(t|c)'
            i_motif_form = [
                '{Y}c{{{n}}}g{X}{{2}}{Y}c{{{m}}}g{X}{{1,}}{Y}c{{{n}}}g{X}{{2}}{Y}c{{{m}}}g',
                'c{{{n}}}{X}{{3,}}c{{{m}}}{X}{{3,}}c{{{n}}}{X}{{3,}}c{{{m}}}',
            ]
            pattern = i_motif_form[1].format(Y=y_symbol, X=x_group, n=n, m=m) if biological_significance else \
                i_motif_form[0].format(Y=y_symbol, X=x_group, n=n, m=m)

            return rstr.xeger(pattern)

        def i_motif_max_strength(string, biological_significance=False):
            x_group = '(a|c|g|t)'
            y_symbol = '(t|c)'
            i_motif_form = [
                '{Y}c{{1,}}g{X}{{2}}{Y}c{{1,}}g',
                'c{{{n}}}{X}{{3,}}c{{{m}}}{X}{{3,}}c{{{n}}}{X}{{3,}}c{{{m}}}',
            ]
            print(i_motif_form[0].format(Y=y_symbol, X=x_group))
            if not biological_significance:
                pattern = i_motif_form[1].format(Y=y_symbol, X=x_group)

            else:
                pattern = i_motif_form[1].format(Y=y_symbol, X=x_group)
            return 0

        a = i_motif_random_string(2, 2)
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
