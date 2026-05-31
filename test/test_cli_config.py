import unittest

from dafna.cli.config import (
    ConfigError,
    DEFAULT_STR_MAX,
    DEFAULT_STR_MIN,
    parse_config,
)


def _parse(text):
    return parse_config(text)


class TestConfigParser(unittest.TestCase):
    def test_full_config(self):
        text = """
        &GQD T
        TOP=[canonical,tandem]
        STR_MIN=2
        STR_MAX=4
        &END

        &IMT T
        &END

        &GEN
        PROJECT=demo
        MODE=gen
        LEN=20
        OUT=out.log
        NCPU=4
        MEM=8GB
        &END
        """
        config = _parse(text)

        gqd = config.structures["GQD"]
        self.assertTrue(gqd.enabled)
        self.assertEqual(gqd.topologies, ["canonical", "tandem"])
        self.assertEqual((gqd.str_min, gqd.str_max), (2, 4))

        imt = config.structures["IMT"]
        self.assertTrue(imt.enabled)
        self.assertIsNone(imt.topologies)  # 'all'
        self.assertEqual((imt.str_min, imt.str_max), (DEFAULT_STR_MIN, DEFAULT_STR_MAX))

        g = config.general
        self.assertEqual(g.project, "demo")
        self.assertEqual(g.mode, "gen")
        self.assertEqual(g.length, 20)
        self.assertEqual(g.out, "out.log")
        self.assertEqual(g.ncpu, 4)
        self.assertEqual(g.mem, "8GB")

    def test_defaults(self):
        config = _parse("&GQD T\n&END\n")
        gqd = config.structures["GQD"]
        self.assertEqual((gqd.str_min, gqd.str_max), (DEFAULT_STR_MIN, DEFAULT_STR_MAX))
        self.assertIsNone(gqd.topologies)
        g = config.general
        self.assertEqual(g.project, "dafna")
        self.assertEqual(g.mode, "gen")
        self.assertIsNone(g.length)  # MIN
        self.assertIsNone(g.out)
        self.assertEqual(g.ncpu, 1)

    def test_flag_variants(self):
        self.assertTrue(_parse("&GQD T\n&END").structures["GQD"].enabled)
        self.assertTrue(_parse("&GQD true\n&END").structures["GQD"].enabled)
        self.assertTrue(_parse("&GQD 1\n&END").structures["GQD"].enabled)
        self.assertFalse(_parse("&GQD F\n&END").structures["GQD"].enabled)
        self.assertFalse(_parse("&GQD\n&END").structures["GQD"].enabled)

    def test_comments_and_blank_lines(self):
        text = """
        # a leading comment
        &GQD T   # enable quadruplexes
          STR_MIN=2  # trailing comment

        &END
        """
        config = _parse(text)
        self.assertTrue(config.structures["GQD"].enabled)
        self.assertEqual(config.structures["GQD"].str_min, 2)

    def test_len_min(self):
        self.assertIsNone(_parse("&GEN\nLEN=MIN\n&END").general.length)
        self.assertIsNone(_parse("&GEN\nLEN=min\n&END").general.length)
        self.assertEqual(_parse("&GEN\nLEN=15\n&END").general.length, 15)

    def test_mode_scan(self):
        g = _parse("&GEN\nMODE=scan\nIN=x.fa\n&END").general
        self.assertEqual(g.mode, "scan")
        self.assertEqual(g.input_path, "x.fa")

    def test_topology_all(self):
        self.assertIsNone(_parse("&GQD T\nTOP=all\n&END").structures["GQD"].topologies)

    def test_topology_dedup(self):
        tops = _parse("&GQD T\nTOP=[canonical,canonical,tandem]\n&END").structures["GQD"].topologies
        self.assertEqual(tops, ["canonical", "tandem"])

    # --- error cases ---

    def test_unknown_block(self):
        with self.assertRaises(ConfigError):
            _parse("&FOO T\n&END")

    def test_unknown_structure_key(self):
        with self.assertRaises(ConfigError):
            _parse("&GQD T\nBOGUS=1\n&END")

    def test_unknown_general_key(self):
        with self.assertRaises(ConfigError):
            _parse("&GEN\nBOGUS=1\n&END")

    def test_unknown_topology(self):
        with self.assertRaises(ConfigError):
            _parse("&GQD T\nTOP=[helix]\n&END")

    def test_strmin_gt_strmax(self):
        with self.assertRaises(ConfigError):
            _parse("&GQD T\nSTR_MIN=5\nSTR_MAX=2\n&END")

    def test_end_without_block(self):
        with self.assertRaises(ConfigError):
            _parse("&END")

    def test_unclosed_block(self):
        with self.assertRaises(ConfigError):
            _parse("&GQD T\nSTR_MIN=2\n")

    def test_assignment_outside_block(self):
        with self.assertRaises(ConfigError):
            _parse("STR_MIN=2\n")

    def test_duplicate_block(self):
        with self.assertRaises(ConfigError):
            _parse("&GQD T\n&END\n&GQD F\n&END")

    def test_nested_block(self):
        with self.assertRaises(ConfigError):
            _parse("&GQD T\n&IMT T\n&END\n&END")

    def test_bad_int(self):
        with self.assertRaises(ConfigError):
            _parse("&GQD T\nSTR_MIN=abc\n&END")

    def test_bad_mode(self):
        with self.assertRaises(ConfigError):
            _parse("&GEN\nMODE=fly\n&END")


class TestRunnableValidation(unittest.TestCase):
    def test_no_structures_enabled(self):
        config = _parse("&GQD F\n&END\n&GEN\nMODE=gen\n&END")
        with self.assertRaises(ConfigError):
            config.validate_runnable()

    def test_scan_requires_input(self):
        config = _parse("&GQD T\n&END\n&GEN\nMODE=scan\n&END")
        with self.assertRaises(ConfigError):
            config.validate_runnable()

    def test_gen_ok(self):
        config = _parse("&GQD T\n&END\n&GEN\nMODE=gen\n&END")
        config.validate_runnable()  # should not raise


if __name__ == "__main__":
    unittest.main()
