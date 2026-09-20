import unittest
import rstr
import src.dafna.lib.strength.strength as strength


class TestIMotif(unittest.TestCase):
    def test_01(self):
        generator = range(3, 5)

        def i_motif_random_string(n, m):
            x_group = '(a|g|t|c)'
            y_symbol = '(t|c)'
            i_motif_form = 'c{{{n}}}{X}{{1}}c{{{m}}}{X}{{1}}c{{{n}}}{X}{{1}}c{{{m}}}'
            pattern = i_motif_form.format(Y=y_symbol, X=x_group, n=n, m=m)

            return rstr.xeger(pattern)

        biological_significance_strings = [i_motif_random_string(n, n + 2) for n in generator]

        self.assertEqual([(n + n + 2) / 2 for n in list(generator)],
                         [strength.i_motif_max_strength(i_motif, True) for i_motif in
                          biological_significance_strings])

        # 'cggcctcctcctcctcgg' holds four 'cc' blocks (offsets 3, 6, 9, 12)
        # separated by single symbols, i.e. c{2}.+c{2}.+c{2}.+c{2} -> 2.0.
        # The old regex checker was anchored to the leftmost match ('c' at
        # offset 0) and reported 1.5.
        self.assertEqual(
            [2, 3, 2, 2.5],
            [
                strength.i_motif_max_strength(i_motif) for i_motif in [
                    'cctttcctttcctttcc',
                    'cccaatcccaatcccaatccc',
                    'cggcctcctcctcctcgg',
                    'cccaatccaatcccaatcc'
                ]
            ]
        )
