import unittest

from dafna.lib import registry
from dafna.lib.registry import RegistryError, StructureDef
from dafna.shared import pintersect, psum


def _gen_strengths(sd, topology, strength, cap=60):
    ctx = sd.make_context()
    result = pintersect(psum(sd.generators[topology](strength, ctx)))
    out = []
    for i, seq in enumerate(result.min_strings()):
        out.append(sd.strength_fn(seq))
        if i >= cap:
            break
    return out


class TestBuiltins(unittest.TestCase):
    def test_builtins_registered(self):
        self.assertEqual(sorted(registry.all_names()), ["GQD", "HRP", "IMT", "TRX"])

    def test_gqd_topologies(self):
        self.assertEqual(sorted(registry.get("GQD").topologies), ["canonical", "tandem"])

    def test_each_generator_matches_its_strength(self):
        cases = [
            ("GQD", "canonical", range(2, 4)),
            ("GQD", "tandem", range(2, 4)),
            ("IMT", "canonical", range(2, 4)),
            ("HRP", "canonical", range(2, 5)),
            ("TRX", "canonical", range(1, 4)),
        ]
        for name, topo, rng in cases:
            sd = registry.get(name)
            for s in rng:
                vals = _gen_strengths(sd, topo, s)
                self.assertTrue(vals, f"{name}/{topo}@{s} produced no strings")
                self.assertTrue(
                    all(v == s for v in vals),
                    f"{name}/{topo}@{s}: strengths {set(vals)} != {s}",
                )


class TestRegisterUnregister(unittest.TestCase):
    def tearDown(self):
        registry.unregister("TMPX")

    def test_register_and_get(self):
        sd = registry.make_template_structure("TMPX", "X* a{s} X*", strength_fn=lambda s: s.count("a"))
        registry.register(sd)
        self.assertTrue(registry.is_registered("TMPX"))
        self.assertIs(registry.get("TMPX"), sd)

    def test_duplicate_rejected(self):
        sd = registry.make_template_structure("TMPX", "X* a{s} X*")
        registry.register(sd)
        with self.assertRaises(RegistryError):
            registry.register(registry.make_template_structure("TMPX", "X* c{s} X*"))

    def test_replace(self):
        registry.register(registry.make_template_structure("TMPX", "X* a{s} X*"))
        sd2 = registry.make_template_structure("TMPX", "X* c{s} X*")
        registry.register(sd2, replace=True)
        self.assertIs(registry.get("TMPX"), sd2)

    def test_no_generators_rejected(self):
        with self.assertRaises(RegistryError):
            registry.register(StructureDef(name="EMPTY", generators={}))

    def test_unknown_get(self):
        with self.assertRaises(RegistryError):
            registry.get("NOPE")


class TestMembership(unittest.TestCase):
    def test_membership_strength(self):
        hrp = registry.get("HRP")
        self.assertEqual(registry.membership_strength(hrp, "aaagggttt", 2, 5), 3)
        self.assertEqual(registry.membership_strength(hrp, "cccccccc", 2, 5), 0)


class TestTemplateStructure(unittest.TestCase):
    def test_template_quadruplex_measured_by_gqd(self):
        quad = registry.make_template_structure("MYQUAD", "X* g{s} X+ g{s} X+ g{s} X+ g{s} X*")
        gqd = registry.get("GQD")
        for s in (2, 3):
            ctx = quad.make_context()
            result = pintersect(psum(quad.generators["canonical"](s, ctx)))
            vals = [gqd.strength_fn(seq) for i, seq in enumerate(result.min_strings()) if i < 40]
            self.assertTrue(vals and all(v == s for v in vals), f"MYQUAD@{s}: {set(vals)}")


if __name__ == "__main__":
    unittest.main()
