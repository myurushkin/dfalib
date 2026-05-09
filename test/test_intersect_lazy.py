import unittest

from dafna.shared import Context, Automata, pintersect


def make_ctx():
    ctx = Context()
    ctx.create_pattern('a|c|g|t', simple=True, name='X')
    return ctx


class TestIntersectLazy(unittest.TestCase):

    PAIRS = [
        ('aXa', 'aXt'),
        ('aXa', 'Xaa'),
        ('aXXa', 'XaaX'),
        ('aXcXt', 'tXcXa'),
        ('XggX', 'aXa'),
    ]

    def _build(self, ctx, expr):
        return ctx.create_pattern(expr)

    def test_lazy_matches_eager_min_strings(self):
        for left, right in self.PAIRS:
            with self.subTest(left=left, right=right):
                ctx_e = make_ctx()
                p1_e = self._build(ctx_e, left)
                p2_e = self._build(ctx_e, right)
                eager = pintersect([p1_e, p2_e], lazy=False)

                ctx_l = make_ctx()
                p1_l = self._build(ctx_l, left)
                p2_l = self._build(ctx_l, right)
                lazy = pintersect([p1_l, p2_l], lazy=True)

                self.assertEqual(set(eager.min_strings()), set(lazy.min_strings()))

    def test_lazy_method_matches_eager_method(self):
        for left, right in self.PAIRS:
            with self.subTest(left=left, right=right):
                ctx_e = make_ctx()
                eager = self._build(ctx_e, left).intersect(
                    self._build(ctx_e, right)
                ).minimize()

                ctx_l = make_ctx()
                lazy = self._build(ctx_l, left).intersect_lazy(
                    self._build(ctx_l, right)
                ).minimize()

                self.assertEqual(set(eager.min_strings()), set(lazy.min_strings()))

    def test_lazy_state_count_le_eager_before_minimize(self):
        for left, right in self.PAIRS:
            with self.subTest(left=left, right=right):
                ctx_e = make_ctx()
                eager = self._build(ctx_e, left).intersect(self._build(ctx_e, right))
                eager_states = eager.state_count()

                ctx_l = make_ctx()
                lazy = self._build(ctx_l, left).intersect_lazy(self._build(ctx_l, right))
                lazy_states = lazy.state_count()

                self.assertLessEqual(lazy_states, eager_states)


if __name__ == "__main__":
    unittest.main()
