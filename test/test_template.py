import unittest

from dafna.lib.generation.template import (
    TemplateError,
    expand_template,
    make_template_generator,
)


class TestTemplateExpansion(unittest.TestCase):
    def test_simple_count(self):
        self.assertEqual(expand_template("g{s}", 3), "ggg")

    def test_count_in_pattern(self):
        self.assertEqual(expand_template("X* g{s} X+ g{s} X*", 2), "X* gg X+ gg X*")

    def test_group_count(self):
        self.assertEqual(expand_template("(gc){2*s}", 2), "gcgcgcgc")

    def test_arithmetic(self):
        self.assertEqual(expand_template("g{s+1}", 2), "ggg")
        self.assertEqual(expand_template("g{2*s-1}", 3), "ggggg")

    def test_zero_count(self):
        self.assertEqual(expand_template("aX*g{s}", 0), "aX*")

    def test_no_placeholders(self):
        self.assertEqual(expand_template("X*ggX*", 5), "X*ggX*")

    def test_unsafe_expr_rejected(self):
        with self.assertRaises(TemplateError):
            expand_template("g{__import__}", 1)
        with self.assertRaises(TemplateError):
            expand_template("g{s.__class__}", 1)

    def test_negative_count_rejected(self):
        with self.assertRaises(TemplateError):
            expand_template("g{s-5}", 1)

    def test_empty_expr_rejected(self):
        with self.assertRaises(TemplateError):
            expand_template("g{}", 1)

    def test_generator_factory(self):
        gen = make_template_generator("X* a{s} X*")
        self.assertTrue(callable(gen))


if __name__ == "__main__":
    unittest.main()
