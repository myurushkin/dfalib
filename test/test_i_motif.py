import random
import regex
import unittest
import rstr
import pprint
import dafna


class TestIMotif(unittest.TestCase):
    def test_01(self):
        generator = range(2, 21)

        def i_motif_random_string(n, m, biological_significance=False):
            x_group = '(a|c|g|t)'
            y_symbol = '(t|c)'
            i_motif_form = [
                '{Y}c{{{n}}}g{X}{{2}}{Y}c{{{m}}}g{X}{{1}}{Y}c{{{n}}}g{X}{{2}}{Y}c{{{m}}}g',
                'c{{{n}}}{X}{{3}}c{{{m}}}{X}{{3}}c{{{n}}}{X}{{3}}c{{{m}}}',
            ]
            pattern = i_motif_form[1].format(Y=y_symbol, X=x_group, n=n, m=m) if biological_significance else \
                i_motif_form[0].format(Y=y_symbol, X=x_group, n=n, m=m)

            return rstr.xeger(pattern)

        def i_motif_max_strength(string, biological_significance: bool = False):

            def get_i_motif_pattern(biological_significance: bool):
                x_group = '[a|c|g|t]'
                y_symbol = '[t|c]'
                patterns = [
                    [
                        '({Y}(c{{1,}})g{X}{{2}}{Y}(c{{1,}})g{X}{{1,}}?{Y}()\\2g{X}{{2}}{Y}()\\3g)',
                        '({Y}(c{{1,}})g{X}{{2}}{Y}(c{{1,}}+)g{X}{{1,}}?{Y}()\\2g{X}{{2}}{Y}()\\3g)'
                    ],
                    [
                        '((c{{3,}}){X}{{3,}}?(c{{1,}}+){X}{{3,}}?()\\2{X}{{3,}}?()\\3)',
                        '((c{{3,}}){X}{{3,}}?(c{{1,}}){X}{{3,}}?()\\2{X}{{3,}}?()\\3)'
                    ]

                ]
                return [pat.format(Y=y_symbol, X=x_group) for pat in patterns[bool(biological_significance)]]

            pattern = get_i_motif_pattern(biological_significance)
            match = [regex.findall(pat, string) for pat in pattern]
            if match:
                return max([(len(mat[1])+len(mat[2]))/2 for pair_mat in match for mat in pair_mat])
            return 0

        # a = [i_motif_random_string(n, n + 1) for n in range(2, 6)]
        b = [i_motif_random_string(n, n+2, True) for n in range(3, 10)]
        pprint.pprint(b)
        pprint.pprint(
            [dafna.strengh.max_imotiv_stength(bi) for bi in b]
        )
        i_motif_max_strength('cccctgcccctaccccgtacccc', True)

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
