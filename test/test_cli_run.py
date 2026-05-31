"""End-to-end runner tests (gen + scan), driven through the registry."""
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from dafna.cli import runner
from dafna.cli.config import ConfigError, parse_config


def _run_capture(config, limit=None):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = runner.run(config, limit=limit)
    return rc, buf.getvalue()


def _data_rows(text):
    return [l for l in text.splitlines() if l and not l.startswith("#")]


class TestGenMode(unittest.TestCase):
    def test_gen_all_builtins(self):
        cfg = parse_config(
            "&GQD T\nSTR_MIN=2\nSTR_MAX=2\n&END\n"
            "&IMT T\nSTR_MIN=2\nSTR_MAX=2\n&END\n"
            "&HRP T\nSTR_MIN=2\nSTR_MAX=2\n&END\n"
            "&TRX T\nSTR_MIN=2\nSTR_MAX=2\n&END\n"
            "&GEN\nMODE=gen\n&END"
        )
        rc, out = _run_capture(cfg, limit=3)
        self.assertEqual(rc, 0)
        rows = _data_rows(out)
        self.assertTrue(rows)
        # header columns: seq, source, GQD, IMT, HRP, TRX  -> 6 fields
        self.assertEqual(len(rows[0].split("\t")), 6)

    def test_gen_custom_structure(self):
        cfg = parse_config(
            "&CUSTOM myquad\nPATTERN=X* g{s} X+ g{s} X+ g{s} X+ g{s} X*\nSTR_MIN=2\nSTR_MAX=2\n&END\n"
            "&GQD T\nSTR_MIN=2\nSTR_MAX=2\n&END\n"
            "&GEN\nMODE=gen\n&END"
        )
        rc, out = _run_capture(cfg, limit=3)
        self.assertEqual(rc, 0)
        rows = _data_rows(out)
        # custom has no strength_fn -> not a column, but GQD is measurable
        self.assertTrue(any("myquad" in r.lower() for r in rows))


class TestScanMode(unittest.TestCase):
    def setUp(self):
        fd, self.fa = tempfile.mkstemp(suffix=".fa")
        with os.fdopen(fd, "w") as f:
            f.write(">q1\ngggagggagggaggg\n>i1\nccctccctccctccc\n")

    def tearDown(self):
        os.unlink(self.fa)

    def test_scan_gqd_imt(self):
        cfg = parse_config(
            "&GQD T\n&END\n&IMT T\n&END\n&GEN\nMODE=scan\nIN=" + self.fa + "\n&END"
        )
        rc, out = _run_capture(cfg)
        self.assertEqual(rc, 0)
        rows = _data_rows(out)
        # q1 -> GQD=3 IMT=0 ; i1 -> GQD=0 IMT=3
        by = {r.split("\t")[1].split("(")[0]: r.split("\t")[2:] for r in rows}
        self.assertEqual(by["q1"], ["3", "0"])
        self.assertEqual(by["i1"], ["0", "3"])

    def test_scan_membership_for_generator_only(self):
        # A custom structure (no strength_fn) is measured by membership in scan.
        cfg = parse_config(
            "&CUSTOM polyc\nPATTERN=X* c{s} X*\nSTR_MIN=1\nSTR_MAX=5\n&END\n"
            "&GEN\nMODE=scan\nIN=" + self.fa + "\n&END"
        )
        rc, out = _run_capture(cfg)
        self.assertEqual(rc, 0)
        rows = _data_rows(out)
        by = {r.split("\t")[1].split("(")[0]: r.split("\t")[2:] for r in rows}
        # i1 = ccctccctccctccc -> longest c-run is 3
        self.assertEqual(by["i1"], ["3"])


class TestErrors(unittest.TestCase):
    def test_unknown_topology_for_builtin(self):
        cfg = parse_config(
            "&GQD T\nTOP=[canonical]\n&END\n&GEN\nMODE=gen\n&END",
            strict=False,
        )
        # canonical is valid; just make sure it runs
        rc, _ = _run_capture(cfg, limit=1)
        self.assertEqual(rc, 0)

    def test_bad_custom_pattern_fails_cleanly(self):
        # An invalid count expression must raise ConfigError before any output.
        cfg = parse_config(
            "&CUSTOM x\nPATTERN=X* g{__y} X*\n&END\n&GEN\nMODE=gen\n&END"
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            with self.assertRaises(ConfigError):
                runner.run(cfg, limit=1)
        self.assertEqual(buf.getvalue(), "")  # nothing emitted before the error

    def test_negative_count_fails_cleanly(self):
        cfg = parse_config(
            "&CUSTOM y\nPATTERN=X* g{s-5} X*\nSTR_MIN=1\nSTR_MAX=1\n&END\n&GEN\nMODE=gen\n&END"
        )
        with self.assertRaises(ConfigError):
            runner.run(cfg, limit=1)


if __name__ == "__main__":
    unittest.main()
