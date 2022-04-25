import unittest
import rstr
import dafna


class TestTriplexes(unittest.TestCase):
    def test_01(self):
        generator = range(2, 10)

        def triplex_random_string(strength):
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
                view.format(X=x_group, count=strength, **triplex_items) for view in triplex_views
                for triplex_items in triplex_groups_options
            ]

            return [rstr.xeger(triplex) for triplex in patterns]

        for i in generator:
            self.assertEqual([i for _ in range(8)], [dafna.triplex_max_strength(triplex) for triplex in triplex_random_string(i)])
        # pprint.pprint([item for item in zip(a, [dafna.triplex_max_strength(s) for s in a])])