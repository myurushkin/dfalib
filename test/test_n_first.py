import unittest

from dafna.shared import Context


def make_ctx():
    ctx = Context()
    ctx.create_pattern('a|c|g|t', simple=True, name='X')
    return ctx


class TestNFirst(unittest.TestCase):

    def test_full_when_limit_exceeds_actual(self):
        ctx = make_ctx()
        p = ctx.create_pattern('aXa').minimize()
        full = list(p.min_strings())
        n10 = list(p.min_strings(n_limit=10))
        self.assertEqual(set(n10), set(full))
        self.assertEqual(len(full), 4)

    def test_limit_truncates(self):
        ctx = make_ctx()
        p = ctx.create_pattern('aXa').minimize()
        for n in (1, 2, 3, 5, 10):
            with self.subTest(n=n):
                got = list(p.min_strings(n_limit=n))
                self.assertLessEqual(len(got), n)

    def test_subset_of_full(self):
        ctx = make_ctx()
        p = ctx.create_pattern('aXa').minimize()
        full = set(p.min_strings())
        for n in (1, 2, 3, 5, 10):
            with self.subTest(n=n):
                got = set(p.min_strings(n_limit=n))
                self.assertTrue(got.issubset(full))

    def test_singleton_min_string_does_not_explode(self):
        ctx = make_ctx()
        p = ctx.create_pattern('aaa').minimize()
        full = list(p.min_strings())
        self.assertEqual(len(full), 1)
        n10 = list(p.min_strings(n_limit=10))
        self.assertEqual(set(n10), set(full))

    def test_n_first_subset_on_richer_dfa(self):
        ctx = make_ctx()
        p = ctx.create_pattern('XXX').minimize()
        full = set(p.min_strings())
        self.assertGreater(len(full), 4)
        for n in (1, 3, 7):
            with self.subTest(n=n):
                got = list(p.min_strings(n_limit=n))
                self.assertLessEqual(len(got), n)
                self.assertTrue(set(got).issubset(full))


if __name__ == "__main__":
    unittest.main()
