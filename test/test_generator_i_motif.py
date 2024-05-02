import random
import unittest
import rstr
from dafna.lib.strength import strength
from dafna.lib.generation import i_motif_gen
from dafna.shared import *

class TestGeneratorIMotif(unittest.TestCase):
    def test_00_canonical_simple(self):
        
        n = 3
        m = 2
        a = 2
        b = 3
        c = 3
        
        ctx = Context()
        patterns = i_motif_gen.create(n=n, m=m, a=a, b=b, c=c, ctx=ctx)
        result: Automata = pintersect(psum(patterns))
            
        for string in result.min_strings():
            print(string)
            
            # NOTE: считаем одну пару CC за 0.5
            self.assertAlmostEqual(i_motif_max_strength(string), (n + m)/2)
            