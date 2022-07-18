import unittest
import rstr
import dafna


class TestIMotif(unittest.TestCase):
    def test_01(self):
        generator = range(3, 21)

        def i_motif_random_string(n, m, biological_significance=False):
            x_group = '(a|g|t|c)'
            y_symbol = '(t|c)'
            i_motif_form = [
                '{Y}c{{{n}}}g{X}{{2}}{Y}c{{{m}}}g{X}{{1}}{Y}c{{{n}}}g{X}{{2}}{Y}c{{{m}}}g',
                'c{{{n}}}{X}{{3}}c{{{m}}}{X}{{3}}c{{{n}}}{X}{{3}}c{{{m}}}',
            ]
            pattern = i_motif_form[1].format(Y=y_symbol, X=x_group, n=n, m=m) if biological_significance else \
                i_motif_form[0].format(Y=y_symbol, X=x_group, n=n, m=m)

            return rstr.xeger(pattern)

        biological_significance_strings = [i_motif_random_string(n, n + 2, True) for n in generator]
        no_biological_significance_strings = [i_motif_random_string(n, n + 2, False) for n in generator]

        self.assertEqual([(n + n + 2) / 2 for n in list(generator)],
                         [dafna.i_motif_max_strength(i_motif, True) for i_motif in biological_significance_strings])
        self.assertEqual([(n + n + 2) / 2 for n in list(generator)],
                         [dafna.i_motif_max_strength(i_motif, False) for i_motif in no_biological_significance_strings])
