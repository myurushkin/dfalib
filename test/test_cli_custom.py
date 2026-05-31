import unittest

from dafna.cli.config import ConfigError, parse_config


class TestCustomBlock(unittest.TestCase):
    def test_custom_basic(self):
        text = """
        &CUSTOM myquad
        PATTERN=X* g{s} X+ g{s} X*
        STR_MIN=2
        STR_MAX=4
        &END
        """
        cfg = parse_config(text)
        s = cfg.structures["MYQUAD"]
        self.assertTrue(s.is_custom)
        self.assertTrue(s.enabled)  # custom is enabled by default
        self.assertEqual(s.pattern, "X* g{s} X+ g{s} X*")
        self.assertEqual((s.str_min, s.str_max), (2, 4))

    def test_custom_disabled_flag(self):
        cfg = parse_config("&CUSTOM myquad F\nPATTERN=X*g{s}X*\n&END")
        self.assertFalse(cfg.structures["MYQUAD"].enabled)

    def test_custom_simple_patterns(self):
        text = """
        &CUSTOM weird
        PATTERN=X* Z{s} X*
        SIMPLE=Z:a|c
        &END
        """
        cfg = parse_config(text)
        self.assertEqual(cfg.structures["WEIRD"].simple, {"Z": "a|c"})

    def test_custom_simple_equals_form(self):
        cfg = parse_config("&CUSTOM w\nPATTERN=Z{s}\nSIMPLE=Z=a|c\n&END")
        self.assertEqual(cfg.structures["W"].simple, {"Z": "a|c"})

    def test_custom_missing_pattern(self):
        with self.assertRaises(ConfigError):
            parse_config("&CUSTOM myquad\nSTR_MIN=2\n&END")

    def test_custom_needs_name(self):
        with self.assertRaises(ConfigError):
            parse_config("&CUSTOM\nPATTERN=X*g{s}X*\n&END")

    def test_custom_reserved_name(self):
        with self.assertRaises(ConfigError):
            parse_config("&CUSTOM gqd\nPATTERN=X*g{s}X*\n&END")

    def test_custom_unknown_key(self):
        with self.assertRaises(ConfigError):
            parse_config("&CUSTOM m\nPATTERN=X*g{s}X*\nBOGUS=1\n&END")

    def test_custom_empty_pattern(self):
        with self.assertRaises(ConfigError):
            parse_config("&CUSTOM m\nPATTERN=\n&END")

    def test_duplicate_custom(self):
        with self.assertRaises(ConfigError):
            parse_config("&CUSTOM m\nPATTERN=X*g{s}X*\n&END\n&CUSTOM m\nPATTERN=X*c{s}X*\n&END")


class TestPluginField(unittest.TestCase):
    def test_plugin_single(self):
        cfg = parse_config("&GEN\nPLUGIN=mypkg.mod\n&END")
        self.assertEqual(cfg.general.plugins, ["mypkg.mod"])

    def test_plugin_comma_list(self):
        cfg = parse_config("&GEN\nPLUGIN=a.b, c.d\n&END")
        self.assertEqual(cfg.general.plugins, ["a.b", "c.d"])


class TestKnownTopologies(unittest.TestCase):
    def test_strict_unknown_block_rejected(self):
        with self.assertRaises(ConfigError):
            parse_config("&FOO T\n&END", strict=True)

    def test_lenient_unknown_block_accepted(self):
        cfg = parse_config("&FOO T\n&END", strict=False)
        self.assertIn("FOO", cfg.structures)

    def test_known_topologies_validation(self):
        known = {"FOO": ["alpha", "beta"]}
        cfg = parse_config("&FOO T\nTOP=[alpha]\n&END", known_topologies=known, strict=True)
        self.assertEqual(cfg.structures["FOO"].topologies, ["alpha"])
        with self.assertRaises(ConfigError):
            parse_config("&FOO T\nTOP=[gamma]\n&END", known_topologies=known, strict=True)


if __name__ == "__main__":
    unittest.main()
