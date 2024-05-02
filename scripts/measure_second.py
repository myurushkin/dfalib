import random
import rstr
from dafna.lib.strength import gqd_canonical, gqd_tandem_repeats
from dafna.lib.generation import gqd_canonocal_gen, gqd_tandem_repeats_gen, i_motif_gen
from dafna.shared import *
from dataclasses import dataclass
from typing import *

@dataclass
class Candidate:
    string: str
    gqd_strength: int
    i_motif_strength: int
    hairpin_strength: int
    triplex_strength: int
    
    def __lt__(self, other):
        # Comparison logic for four attributes
        return (self.gqd_strength < other.gqd_strength and self.i_motif_strength <= other.i_motif_strength and self.hairpin_strength <= other.hairpin_strength and self.triplex_strength <= other.triplex_strength) or \
               (self.gqd_strength <= other.gqd_strength and self.i_motif_strength < other.i_motif_strength and self.hairpin_strength <= other.hairpin_strength and self.triplex_strength <= other.triplex_strength) or \
               (self.gqd_strength <= other.gqd_strength and self.i_motif_strength <= other.i_motif_strength and self.hairpin_strength < other.hairpin_strength and self.triplex_strength <= other.triplex_strength) or \
               (self.gqd_strength <= other.gqd_strength and self.i_motif_strength <= other.i_motif_strength and self.hairpin_strength <= other.hairpin_strength and self.triplex_strength < other.triplex_strength)

def pareto_optimal(items):
    pareto_set = []
    for item in items:
        is_dominated = False
        for other in pareto_set:
            if other < item:
                is_dominated = True
                break
        if not is_dominated:
            pareto_set = [x for x in pareto_set if not item < x]
            pareto_set.append(item)
    return pareto_set

if __name__ == "__main__":
    
    ctx = Context()
    X = ctx.create_pattern("a|c|g|t", simple=True, name="X")
     
    i_motifs_patterns = []
    for n in [2, 3, 4]:
        for m in [2, 3, 4]:
            for a in [1, 2, 3]:
                for b in [1, 2, 3]:
                    for c in [1, 2, 3]:
                        i_motifs_patterns.extend(i_motif_gen.create(n=n, m=m, a=a, b=b, c=c, ctx=ctx))

    gqd_patterns = []
    for strength in [2, 3]:
        gqd_patterns.extend(gqd_canonocal_gen.create(strength=strength, ctx=ctx))
    
    string_size_pattern = ctx.create_pattern('X' * 20)
    
    Y = ctx.create_pattern("a|c|t", simple=True, name="Y")
    for strength in [2, 3]:
        gqd_patterns.extend(gqd_tandem_repeats_gen.create(strength=strength, ctx=ctx))
        
    string_gen: Automata = pintersect(psum(i_motifs_patterns), psum(gqd_patterns), string_size_pattern)
        
    result = []
    for string in string_gen.min_strings():
        gqd_strength = gqd_max_strength(string)
        i_motif_strength = i_motif_max_strength(string)
        hairpin_strength = hairpin_max_strength(string)
        triplex_strength, _ = triplex_max_strength(string)
        
        result.append(Candidate(string=string,
                                gqd_strength=gqd_strength,
                                i_motif_strength=i_motif_strength,
                                hairpin_strength=hairpin_strength,
                                triplex_strength=triplex_strength))
        
        if hairpin_strength > 0:
            print(result[-1])
            
    pareto = pareto_optimal(result)
    
    for p in pareto:
        print(p)
        
               
            
            