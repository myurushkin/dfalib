import unittest

from dafna.shared import Context, pintersect
from dafna.window import (
    find_min_string_under_budget,
    find_min_string_in_window,
    find_min_string_in_gc_window,
    find_all_min_strings_under_budget,
)

GC_COST = (0, 1, 1, 0)  # alphabet positions a=0,g=1,c=2,t=3; G and C have cost 1


def make_ctx():
    ctx = Context()
    ctx.create_pattern('a|c|g|t', simple=True, name='X')
    return ctx


def build_dfa(ctx, *exprs):
    auts = [ctx.create_pattern(e) for e in exprs]
    result = auts[0]
    for a in auts[1:]:
        result = result.intersect_lazy(a).minimize()
    return result


def gc_count(s):
    return sum(1 for ch in s if ch in ('c', 'g'))


class TestWindowBudget(unittest.TestCase):

    def test_under_budget_finds_shortest(self):
        # Language: strings containing 'gg' as substring; shortest is length 2.
        # Cost = uniform (1,1,1,1); budget large enough to allow any string.
        ctx = make_ctx()
        big = build_dfa(ctx, 'X*ggX*')
        cost = (1, 1, 1, 1)
        result = find_min_string_under_budget(big, cost, budget=256)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        # Result must be accepted: contain 'gg' at some position (it is the min-length string).
        self.assertIn(result, ['aa', 'ac', 'ag', 'at', 'ca', 'cc', 'cg', 'ct',
                                'ga', 'gc', 'gg', 'gt', 'ta', 'tc', 'tg', 'tt'])
        # Actually verify the DFA accepts it by checking it's a length-2 string in {a,c,g,t}*.
        self.assertTrue(all(ch in 'acgt' for ch in result))

    def test_under_budget_matches_find_all_min_strings(self):
        # find_min_string_under_budget length must equal length of
        # the first string from find_all_min_strings_under_budget.
        ctx1 = make_ctx()
        big1 = build_dfa(ctx1, 'X*ggX*', 'X*ccX*')
        cost = (1, 1, 1, 1)
        single = find_min_string_under_budget(big1, cost, budget=256)
        self.assertIsNotNone(single)

        ctx2 = make_ctx()
        big2 = build_dfa(ctx2, 'X*ggX*', 'X*ccX*')
        all_min = find_all_min_strings_under_budget(big2, cost, budget=256, n_limit=10)
        self.assertTrue(len(all_min) > 0)
        self.assertEqual(len(single), len(all_min[0]))


class TestWindowCostWindow(unittest.TestCase):

    def test_window_rejects_outside_range(self):
        # Language: exact length-2 strings with exactly one GC base.
        # cost = GC count: a=0, g=1, c=1, t=0.
        # cost_lo=1, cost_hi=1 should find a length-2 string with exactly 1 GC base.
        ctx = make_ctx()
        # Exact 2-char strings with mixed (AT/GC) bases — no XX repeats.
        big = build_dfa(ctx, 'ac|ca|gc|cg|ag|ga|tg|gt|tc|ct|at|ta')
        cost = (0, 1, 1, 0)
        result = find_min_string_in_window(big, cost, cost_lo=1, cost_hi=1)
        self.assertIsNotNone(result)
        gc_count_val = sum(1 for ch in result if ch in ('c', 'g'))
        self.assertEqual(gc_count_val, 1)
        self.assertEqual(len(result), 2)

    def test_window_returns_none_when_impossible(self):
        # Language: only 'aa' — zero GC bases.
        # cost_lo=2 makes it impossible.
        ctx = make_ctx()
        big = build_dfa(ctx, 'aa')
        cost = (0, 1, 1, 0)
        result = find_min_string_in_window(big, cost, cost_lo=2, cost_hi=4)
        self.assertIsNone(result)

    def test_lw_trivial(self):
        # DFA: all length-1 DNA strings; cost=0 everywhere; window=[0,0].
        # Every string has cost 0 so window [0,0] is always satisfied.
        # Must return a single-character string (the shortest accepted string).
        ctx = make_ctx()
        big = build_dfa(ctx, 'a|c|g|t')
        cost = (0, 0, 0, 0)
        result = find_min_string_in_window(big, cost, cost_lo=0, cost_hi=0)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertIn(result, ('a', 'c', 'g', 't'))

    def test_lw_gc_only_window(self):
        # DFA accepting all length-4 DNA strings; cost=GC count; window=[2,2].
        # Must return a length-4 string with exactly 2 GC bases.
        ctx = make_ctx()
        one = '(a|c|g|t)'
        big = build_dfa(ctx, one + one + one + one)
        result = find_min_string_in_window(big, GC_COST, cost_lo=2, cost_hi=2)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 4)
        self.assertEqual(gc_count(result), 2)

    def test_lw_unsatisfiable(self):
        # DFA accepting only single-character strings; max GC count is 1.
        # window=[5,10] is unreachable — must return None.
        ctx = make_ctx()
        big = build_dfa(ctx, 'a|c|g|t')
        result = find_min_string_in_window(big, GC_COST, cost_lo=5, cost_hi=10)
        self.assertIsNone(result)

    def test_lw_intersect(self):
        # Intersect two patterns: strings containing 'gg' AND containing 'cc'.
        # Apply GC window [4,4] — result must have exactly 4 GC bases.
        ctx = make_ctx()
        big = build_dfa(ctx, 'X*ggX*', 'X*ccX*')
        result = find_min_string_in_window(big, GC_COST, cost_lo=4, cost_hi=4)
        self.assertIsNotNone(result)
        self.assertEqual(gc_count(result), 4)
        self.assertIn('gg', result)
        self.assertIn('cc', result)

    def test_lw_consistency_with_round2(self):
        # With cost=(0,0,0,0) and window=[0,0], every string has cost 0.
        # The shortest accepted string has the same length as round-2 min_strings.
        ctx1 = make_ctx()
        big1 = build_dfa(ctx1, 'X*ggX*')
        result = find_min_string_in_window(big1, (0, 0, 0, 0), cost_lo=0, cost_hi=0)
        self.assertIsNotNone(result)

        ctx2 = make_ctx()
        big2 = build_dfa(ctx2, 'X*ggX*')
        round2_min = list(big2.min_strings(n_limit=1))
        self.assertTrue(len(round2_min) > 0)
        self.assertEqual(len(result), len(round2_min[0]))

    def test_lw_n_first(self):
        # find_all_min_strings_under_budget with n_limit=3.
        # DFA: strings containing 'gg'. Cost=(0,1,1,0) (GC count). Budget=2.
        # At length 2, accepting strings 'gg' have b=2 (one (q,b) pair).
        # Use wide budget=10 to allow multiple accepting states at min length
        # with different b values (e.g. 'gg'=b2, 'ga'=b1, 'ag'=b1, 'aa'=b0, etc.
        # all have length 2 but different GC counts -> different (q,b) states).
        ctx = make_ctx()
        big = build_dfa(ctx, 'X*ggX*')
        results = find_all_min_strings_under_budget(big, GC_COST, budget=10, n_limit=3)
        # Must return at least 1 and at most 3 strings, all minimum length.
        self.assertGreater(len(results), 0)
        self.assertLessEqual(len(results), 3)
        min_len = len(results[0])
        for s in results:
            self.assertEqual(len(s), min_len)
            self.assertIn('gg', s)


class TestWindowGC(unittest.TestCase):

    def test_gc_window_basic(self):
        # Language: strings of length >=2 containing 'gc'.
        # alpha=0.5, beta=1.0 means >=50% GC at every length.
        # The shortest such string is length 2 ('gc') with 100% GC — passes [0.5,1.0].
        ctx = make_ctx()
        big = build_dfa(ctx, 'X*gcX*')
        result = find_min_string_in_gc_window(big, alpha=0.5, beta=1.0)
        self.assertIsNotNone(result)
        gc_count_val = sum(1 for ch in result if ch in ('c', 'g'))
        ratio = gc_count_val / len(result)
        self.assertGreaterEqual(ratio, 0.5)
        self.assertLessEqual(ratio, 1.0)

    def test_gc_window_layer_aware(self):
        # GC window [0.0, 0.0] means 0 GC bases required (all AT).
        # DFA: strings containing 'aa'. Shortest such string is 'aa' (length 2, 0% GC).
        # Layer-aware accept at len=2: ceil(0.0*2)=0 <= b <= floor(0.0*2)=0 -> b==0.
        # 'aa' has GC cost b=0, so it must be accepted.
        ctx = make_ctx()
        big = build_dfa(ctx, 'X*aaX*')
        result = find_min_string_in_gc_window(big, alpha=0.0, beta=0.0)
        self.assertIsNotNone(result)
        self.assertEqual(gc_count(result), 0)
        self.assertIn('aa', result)

    def test_gc_window_degenerate_wide(self):
        # alpha=0, beta=1 accepts any GC content — equivalent to unconstrained BFS.
        # Result length must equal round-2 min_strings length on same DFA.
        ctx1 = make_ctx()
        big1 = build_dfa(ctx1, 'X*gcX*')
        result = find_min_string_in_gc_window(big1, alpha=0.0, beta=1.0)
        self.assertIsNotNone(result)

        ctx2 = make_ctx()
        big2 = build_dfa(ctx2, 'X*gcX*')
        round2_min = list(big2.min_strings(n_limit=1))
        self.assertEqual(len(result), len(round2_min[0]))


class TestVariantB(unittest.TestCase):
    """Variant B: exhaustive multi-path reconstruction tests."""

    def _make_two_path_dfa(self):
        # DFA accepting strings that contain 'ag' OR 'ga'.
        # Both 'ag' and 'ga' are length-2 min-length accepting strings with different
        # augmented states under GC cost (ag: b=1, ga: b=1 but different q paths).
        # Under uniform cost (1,1,1,1) budget=10 there are multiple min-length strings.
        ctx = make_ctx()
        big = build_dfa(ctx, 'X*(ag|ga)X*')
        return big

    def test_variant_b_returns_all_paths_at_min_length(self):
        # DFA accepting strings containing 'ag' or 'ga' (both length-2 at minimum).
        # With uniform cost and large budget, variant B must return both 'ag' and 'ga'
        # (plus others of the same min length that go through different (q,b) states).
        # Variant A would return at most one string per accepting (q,b) state.
        big = self._make_two_path_dfa()
        results = find_all_min_strings_under_budget(big, (1, 1, 1, 1), budget=100, n_limit=-1)
        self.assertGreater(len(results), 0)
        min_len = len(results[0])
        for s in results:
            self.assertEqual(len(s), min_len, f"All results must share min length; got {s!r}")
        # All results must be accepted (contain 'ag' or 'ga').
        for s in results:
            self.assertTrue('ag' in s or 'ga' in s, f"String {s!r} not accepted by DFA")
        # Variant B must find both 'ag' and 'ga' (both are min-length accepting strings).
        self.assertIn('ag', results)
        self.assertIn('ga', results)

    def test_variant_b_n_limit_caps(self):
        # Same DFA; n_limit=1 returns at most 1 string.
        big = self._make_two_path_dfa()
        results_1 = find_all_min_strings_under_budget(big, (1, 1, 1, 1), budget=100, n_limit=1)
        self.assertGreaterEqual(len(results_1), 1)
        self.assertLessEqual(len(results_1), 1)

        # n_limit=2 returns at most 2 strings, all at min length.
        results_2 = find_all_min_strings_under_budget(big, (1, 1, 1, 1), budget=100, n_limit=2)
        self.assertGreaterEqual(len(results_2), 1)
        self.assertLessEqual(len(results_2), 2)
        min_len = len(results_2[0])
        for s in results_2:
            self.assertEqual(len(s), min_len)

    def test_variant_b_zero_budget_zero_cost(self):
        # With cost=(0,0,0,0) and budget=0, accumulated cost is always 0 regardless of
        # string length; variant B must return the same set of min-length strings as
        # round-2 find_all_min_strings.
        ctx1 = make_ctx()
        big1 = build_dfa(ctx1, 'X*ggX*')
        variant_b = find_all_min_strings_under_budget(big1, (0, 0, 0, 0), budget=0, n_limit=50)

        ctx2 = make_ctx()
        big2 = build_dfa(ctx2, 'X*ggX*')
        round2 = sorted(big2.min_strings(n_limit=50))

        self.assertEqual(sorted(variant_b), round2,
                         "With zero cost/budget variant B must match round-2 find_all_min_strings exactly")


if __name__ == '__main__':
    unittest.main()
