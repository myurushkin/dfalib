import pprint

import regex
import unittest
import rstr
import dafna


class TestIMotif(unittest.TestCase):
    def test_01(self):
        generator = range(3, 20)

        def i_motif_random_string(n, m, biological_significance=False):
            x_group = '(a|g|t)'
            y_symbol = '(t|c)'
            i_motif_form = [
                '{Y}c{{{n}}}g{X}{{2}}{Y}c{{{m}}}g{X}{{1}}{Y}c{{{n}}}g{X}{{2}}{Y}c{{{m}}}g',
                'c{{{n}}}{X}{{3}}c{{{m}}}{X}{{3}}c{{{n}}}{X}{{3}}c{{{m}}}',
            ]
            pattern = i_motif_form[1].format(Y=y_symbol, X=x_group, n=n, m=m) if biological_significance else \
                i_motif_form[0].format(Y=y_symbol, X=x_group, n=n, m=m)

            return rstr.xeger(pattern)

        def i_motif_max_strength(string, biological_significance: bool = False):
            x_group = '[a|c|g|t]'
            y_symbol = '[t|c]'
            n = '3,'
            m = '1,'
            biological_significance_pattern = '((c{{{n}}}){X}{{3,}}?(c{{{m}}}){X}{{3,}}?()\\2{X}{{3,}}?()\\3)'
            no_biological_significance_pattern = '({Y}(c{{1,}})g{X}{{2}}{Y}(c{{1,}})g{X}{{1}}{Y}()\\2g{X}{{2}}{Y}()\\3g)'

            if biological_significance:
                pattern = biological_significance_pattern.format(Y=y_symbol, X=x_group, n=n, m=m)
                match = regex.findall(pattern, string)
                if any(match):
                    strength = 0
                    for i_motif in match:
                        sub_strength = (len(i_motif[1]) + len(i_motif[2])) / 2
                        for i in i_motif:
                            sub_match = regex.findall(
                                biological_significance_pattern.format(Y=y_symbol, X=x_group, n=i, m=m), string)
                            if any(sub_match):
                                temp_strength = (sub_match[1] + sub_match[2]) / 2
                                sub_strength = sub_strength if sub_strength > temp_strength else temp_strength

                        strength = strength if strength > sub_strength else sub_strength
                    return strength

            else:
                pattern = no_biological_significance_pattern.format(Y=y_symbol, X=x_group)
                match = regex.findall(pattern, string)
                if any(match):
                    strength = 0
                    for i_motif in match:
                        sub_strength = (len(i_motif[1]) + len(i_motif[2])) / 2
                        strength = strength if strength > sub_strength else sub_strength
                    return strength
            return 0

        biological_significance_strings = [i_motif_random_string(n, n + 2, True) for n in generator]
        no_biological_significance_strings = [i_motif_random_string(n, n + 2, False) for n in generator]

        self.assertEqual([(n + n + 2) / 2 for n in list(generator)],
                         [i_motif_max_strength(i_motif, True) for i_motif in biological_significance_strings])
        self.assertEqual([(n + n + 2) / 2 for n in list(generator)],
                         [i_motif_max_strength(i_motif, False) for i_motif in no_biological_significance_strings])
        self.assertEqual(6, i_motif_max_strength('cccccctacccccccccccccccgttccccccc', True))

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
