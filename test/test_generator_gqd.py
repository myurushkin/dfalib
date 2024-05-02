import random
import unittest
import rstr
from dafna.lib.strength import strength
from dafna.lib.strength import gqd_canonical
from dafna.lib.strength import gqd_tandem_repeats
from dafna.lib.generation import gqd_canonocal_gen
from dafna.lib.generation import gqd_tandem_repeats_gen
from dafna.shared import *

class TestGeneratorGQD(unittest.TestCase):
    def test_00_canonical_simple(self):
        input_strengths = [3, 5, 6, 10]
        
        for input_strength in input_strengths:
            ctx = Context()
            X = ctx.create_pattern("a|c|g|t", simple=True, name="X")
            
            patterns = gqd_canonocal_gen.create(input_strength, ctx, X)
            result: Automata = pintersect(psum(patterns))
            
            for string in result.min_strings():
                self.assertEqual(gqd_canonical.gqd_max_strength(string), input_strength)
                
    def test_01_tandem_repeats_simple(self):
        input_strengths = [2, 4]
        
        for input_strength in input_strengths:
            ctx = Context()
            
            Y = ctx.create_pattern("a|c|t", simple=True, name="Y")
            X = ctx.create_pattern("a|c|g|t", simple=True, name="X")
            
            patterns = gqd_tandem_repeats_gen.create(input_strength, ctx, X)
            result: Automata = pintersect(psum(patterns))
            
            for index, string in enumerate(result.min_strings()):
                print(string)
                self.assertEqual(gqd_tandem_repeats.max_strength(string), input_strength)
                if index > 1:
                    break